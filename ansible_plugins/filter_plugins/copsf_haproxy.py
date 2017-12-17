#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import six
import time
import collections
import cProfile
import os
import contextlib
import hashlib
import logging
import fcntl
import copy
import traceback
import tempfile
import random
import string
import re
from distutils.version import LooseVersion
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


OBJECT_SANITIZER = re.compile('[\\\@+\$^&~"#\'()\[\]%*.:/]',
                              flags=re.M | re.U | re.X)
registration_prefix = 'corpusops_haproxy_registrations_registrations_'
DEFAULT_FRONTENDS = {80: {}, 443: {}}


def sanitize(key):
    if isinstance(key, list):
        key = '_'.join(key)
    key = key.replace('*', 'wildcard')
    return OBJECT_SANITIZER.sub('_', key)


def get_object_name(mode, port,
                    prefix='o',
                    host=None,
                    regex=None,
                    wildcard=None,
                    **kwargs):
    name = '{0}{1}_{2}'.format(prefix, mode, port)
    if host:
        key = 'host'
        id_ = host
    elif regex:
        key = 'regex'
        id_ = regex
    elif wildcard:
        key = 'wildcard'
        id_ = wildcard
    else:
        key = None
        id_ = None
    if key:
        name += '_{0}_{1}'.format(key, sanitize(id_))
    return name


def get_backend_name(mode, port,
                     host=None,
                     regex=None,
                     wildcard=None,
                     **kwargs):
    return get_object_name(prefix='b',
                           mode=mode,
                           port=port,
                           host=host,
                           regex=regex,
                           wildcard=wildcard,
                           **kwargs)


def get_frontend_name(mode, port,
                      host=None,
                      regex=None,
                      wildcard=None,
                      **kwargs):
    return get_object_name(prefix='f',
                           mode=mode,
                           port=port,
                           host=host,
                           regex=regex,
                           wildcard=wildcard,
                           **kwargs)


def ordered_backend_opts(opts=None):
    if not opts:
        opts = []
    opts = copy.deepcopy(opts)

    def sort(opt, count={'count': 0}):
        count['count'] += 1
        pref = count['count']
        opt = opt.strip()
        if opt.startswith('balance '):
            pref += 100
        elif opt.startswith('option '):
            pref += 500
        elif opt.startswith('tcp-check '):
            pref += 600
        elif opt.startswith('http-check '):
            pref += 600
        elif opt.startswith('http-request '):
            pref += 700
        elif opt.startswith('timeout '):
            pref += 800

        return '{0:04d}_{1}'.format(pref, opt)

    opts.sort(key=sort)
    return opts


def ordered_frontend_opts(opts=None):
    if not opts:
        opts = []
    opts = copy.deepcopy(opts)

    def sort(opt, count={'count': 0}):
        count['count'] += 1
        pref = count['count']
        opt = opt.strip()
        if opt.startswith('acl '):
            pref += 100
        elif 'use_backend' in opt:
            pref += 500
        elif 'default_backend' in opt:
            pref += 900
        if ' rgx_' in opt:
            pref += 20
        elif ' wc_' in opt:
            pref += 70
            if 'wildcard' in opt:
                pref += 1
        elif ' host_' in opt:
            pref += 50
            if 'wildcard' in opt:
                pref += 1
        return '{0:04d}_{1}'.format(pref, opt)

    opts.sort(key=sort)
    return opts


def register_frontend(data,
                      port,
                      frontends=None,
                      backends=None,
                      mode=None,
                      hosts=None,
                      wildcards=None,
                      regexes=None):
    sbind = '*:{0}'.format(port)
    if not data['no_ipv6']:
        sbind = '{0},ipv6@:{1}'.format(sbind, port)
    # if this is a TLS backend, append also the certificates
    # configured on the machine
    if frontends is None:
        frontends = OrderedDict()
    has = {'backend': False,
           'ssl': False,
           'maincert_path': data['maincert_path'] is not None}
    if mode.startswith('https') or mode in ['tcps', 'ssl', 'tls']:
        has.update({'ssl': True})
        sbind = '{0} ssl {1}'.format(
           sbind,
           data['ssl']['frontend_bind_options'])
    fr = get_frontend_name(mode, port)
    frontend = frontends.setdefault(fr, {})
    frontend.setdefault('bind', sbind)
    # normalise https -> http  & default proxy mode to TCP
    hmode = frontend.setdefault(
        'mode',
        mode.startswith('http') and 'http' or 'tcp')
    opts = frontend.setdefault(
        'raw_opts',
        data['frontend_opts'].get(mode, [])[:])
    # if we are on http/https, use the LEVEL7 haproxy mode
    # TUPLE FOR ORDER IS IMPORTANT !
    # one_backend does not have any importance, its sole purpose is
    # to factorize further code
    if not hmode.startswith('http'):
        aclmodes = (('default', ['one_backend']),)
    else:
        aclmodes = (('regex', regexes),
                    ('wildcard', wildcards),
                    ('host', hosts))
    for aclmode, chosts in aclmodes:
        if chosts:
            for match in chosts:
                has['backend'] = True
                bck_name = get_backend_name(
                    mode, port, **{aclmode: match})
                sane_match = sanitize(match)
                if any([
                    aclmode == 'wildcard' and match == '*',
                    aclmode == 'regex' and match == '.*'
                ]):
                    aclmode = 'default'
                cfgentries = {
                    'default': (
                        [],
                        ['default_backend {bck_name}']),
                    'regex': (
                        ['acl rgx_{sane_match}'
                         ' hdr_reg(host) -i {match[0]} url_reg'
                         ' -i {match[1]}',
                         'acl rgx_{sane_match}'
                         ' hdr_reg(host) -i {match[0]} url_reg'
                         ' -i {match[1]}:{port}'],
                        ['use_backend {bck_name} if rgx_{sane_match}']),
                    'wildcard': (
                        ['acl wc_{sane_match} hdr_end(host) -i {match}',
                         'acl wc_{sane_match} hdr_end(host) -i {match}:{port}'],  #noqa
                        ['use_backend {bck_name} if wc_{sane_match}']),
                    'host': (
                        ['acl host_{sane_match} hdr(host) -i {match}:{port}',
                         'acl host_{sane_match} hdr(host) -i {match}'],
                        ['use_backend {bck_name} if host_{sane_match}']),
                }
                aclsdefs = cfgentries.get(aclmode, cfgentries['default'])
                for acls in aclsdefs:
                    for cfgentry in acls:
                        cfgentry = cfgentry.format(
                            port=port,
                            match=(aclmode == 'wildcard' and
                                   match[2:] or
                                   match),
                            sane_match=sane_match,
                            bck_name=bck_name)
                        if cfgentry not in opts:
                            opts.append(cfgentry)
    if has['ssl'] and not has['maincert_path'] or not has['backend']:
        frontends.pop(fr, None)
    return frontends


def register_servers_to_backends(data,
                                 port,
                                 ip,
                                 to_port=None,
                                 mode='tcp',
                                 user=None,
                                 password=None,
                                 wildcards=None,
                                 regexes=None,
                                 frontends=None,
                                 hosts=None,
                                 backends=None,
                                 ssl_terminated=None,
                                 http_fallback=None):
    '''
    Register a specific minion as a backend server
    where haproxy will forward requests to
    '''
    # if we proxy some https? traffic, we rely on host to choose a backend
    # and in other cases, we assume to proxy to a TCPs? backend
    if ssl_terminated is None:
        ssl_terminated = False
    if http_fallback is None:
        http_fallback = True
    if backends is None:
        backends = OrderedDict()
    sane_ip = sanitize(ip)
    if mode == 'redis' and password is not None:
        mode = 'redis_auth'
    opts = data['backend_opts'].get(
        mode,
        data['backend_opts']['tcp'])
    if not to_port:
        to_port = port
    if mode.startswith('http'):
        hmode = 'http'
        #  we try first a backend over https, and if not present on http #}
        if mode.startswith('https'):
            slug = ' ssl verify none'
            if ssl_terminated:
                slug = ''
            servers = [{'name': 'srv_{0}_ssl'.format(sane_ip),
                        'bind': '{0}:{1}'.format(ip, to_port),
                        'opts': 'check weight 100 inter 1s{0}'.format(slug)}]
            if http_fallback:
                servers.insert(0, {'name': 'srv_{0}_clear'.format(sane_ip),
                                   'bind': '{0}:{1}'.format(ip, 80),
                                   'opts': 'check weight 50 inter 1s backup'})
        else:
            servers = [{'name': 'srv_{0}'.format(sane_ip),
                        'bind': '{0}:{1}'.format(ip, to_port),
                        'opts': 'check inter 1s'}]

    elif mode in [
        'rabbitmq', 'tcp', 'tcps',
        'ssl', 'tls', 'redis', 'redis_auth'
    ]:
        hmode = 'tcp'
        servers = [
               {'name': 'srv_{0}'.format(sane_ip),
                'bind': '{0}:{1}'.format(ip, to_port),
                'opts': 'check inter 1s'}]
    if not hmode.startswith('http'):
        aclmodes = (('default', ['one_backend']),)
    else:
        aclmodes = (('host', hosts),
                    ('regex', regexes),
                    ('wildcard', wildcards))
    for aclmode, hosts in aclmodes:
        if hosts:
            for match in hosts:
                bck_name = get_backend_name(mode, port, **{aclmode: match})
                backend = backends.setdefault(bck_name, {})
                backend.setdefault('mode', hmode)
                bopts = backend.setdefault('raw_opts', [])
                for o in opts:
                    o = o.format(user=user, password=password)
                    if o not in bopts:
                        bopts.append(o)
                bopts = backend['raw_opts']
                bservers = backend.setdefault('servers', [])
                for server in servers:
                    if server not in bservers:
                        bservers.append(server)
    return backends


def make_registrations(data, ansible_vars=None):
    '''
    The idea is to have somehow haproxies-as-a-service
    where minions register themselves up to the haproxies.
    - they can then ve evicted from the proxies
      if they have a grain setted 'haproxy_disable'
    - We search in the pillar and in the mine for any registered frontend
      for each frontend, we try to setup the underling frontend
      and backend objects for the haproxy configuration
    '''
    frontends = data['frontends']
    backends = data['backends']
    proxy_modes = {}
    for m in data["proxy_modes"]:
        proxy_modes["{0}".format(m)] = data["proxy_modes"][m]
    for k in data['registrations']:
        definitions = data['registrations'][k]
        for payload in definitions:
            for port, fdata in payload.get(
                'frontends', DEFAULT_FRONTENDS
            ).items():
                port = int(port)
                sport = "{0}".format(port)
                hosts = payload.get('hosts', [])
                wildcards = payload.get('wildcards', [])
                regexes = payload.get('regexes', [])
                to_port = int(fdata.get('to_port', port))
                user = fdata.get('user', None)
                password = fdata.get('password', None)
                ssl_terminated = fdata.get('ssl_terminated', None)
                http_fallback = fdata.get('http_fallback', None)
                mode = fdata.get('mode', proxy_modes.get(sport, 'tcp'))
                frontends = register_frontend(
                    data, port=port, mode=mode, hosts=hosts,
                    frontends=frontends,
                    backends=backends,
                    wildcards=wildcards,
                    regexes=regexes)
                backends = register_servers_to_backends(
                    data,
                    port=port, ip=payload['ip'],
                    to_port=to_port, mode=mode,
                    user=user, password=password,
                    hosts=hosts, wildcards=wildcards,
                    regexes=regexes,
                    ssl_terminated=ssl_terminated,
                    http_fallback=http_fallback,
                    frontends=frontends,
                    backends=backends)
    return data


__funcs__ = {
    'copshaproxyf_sanitize': sanitize,
    'copshaproxyf_get_object_name': get_object_name,
    'copshaproxyf_get_backend_name': get_backend_name,
    'copshaproxyf_get_frontend_name': get_frontend_name,
    'copshaproxyf_ordered_backend_opts': ordered_backend_opts,
    'copshaproxyf_ordered_frontend_opts': ordered_frontend_opts,
    'copshaproxyf_make_registrations': make_registrations,
}


class FilterModule(object):

    def filters(self):
        return __funcs__
# vim:set et sts=4 ts=4 tw=80
