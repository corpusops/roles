#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from ansible.module_utils import six
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
SSHPROXY = [
  'option tcplog',
  'tcp-request inspect-delay 5s',
  'tcp-request content accept if HTTP',
  'acl client_attempts_ssh payload(0,7) -m bin 5353482d322e30',
  'use_backend {ssh_proxy} if !HTTP',
  'use_backend {ssh_proxy} if client_attempts_ssh',
  'use_backend {http_proxy} if HTTP']


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


def get_ssh_backend_proxy_name(ssh_proxy_host, ssh_proxy_port, k='ssh'):
    return get_backend_name('tcp', ssh_proxy_port, '{0}_{1}'.format(k, ssh_proxy_host))


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
        if 'letsencrypt' in opt and (
            'acl ' in opt or
            'use_backend ' in opt
        ):
            pref = 90
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
                      raw_frontend=None,
                      regexes=None,
                      letsencrypt=None,
                      ssh_proxy=None,
                      ssh_proxy_host=None,
                      ssh_proxy_port=None):
    proxied_port = port
    if ssh_proxy:
        proxied_port = port + 1
    sbind = '*:{0}'.format(port)
    if not data['no_ipv6']:
        sbind = '{0},ipv6@:{1}'.format(sbind, port)
    if ssh_proxy_host is None:
        ssh_proxy_host = '127.0.0.1'
    if ssh_proxy_port is None:
        ssh_proxy_port = 22
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
           data['ssl']['frontend_bind_options'],
           bracket='{', ebracket='}')
    fbind = sbind
    if ssh_proxy:
        fbind = '127.0.0.1:{0}'.format(proxied_port)
    fr = get_frontend_name(mode, proxied_port)
    frontend = frontends.setdefault(fr, {})
    frontend.setdefault('bind', fbind)
    if ssh_proxy:
        ssshbckname = get_ssh_backend_proxy_name(ssh_proxy_host, ssh_proxy_port,
                                               k='ssh')
        hsshbckname = get_ssh_backend_proxy_name('127.0.0.1', proxied_port,
                                               k='https')
        sshfr = get_frontend_name('tcp', port)
        sshproxyfrontend = frontends.setdefault(sshfr, {})
        sshproxyfrontend.setdefault('bind', sbind)
        sshproxyfrontend["mode"] = "tcp"
        sshproxyfrontend["raw_opts"] = [
            a.format(http_proxy=hsshbckname, ssh_proxy=ssshbckname,
                     bracket='{', ebracket='}')
            for a in SSHPROXY]
    if raw_frontend is None:
        raw_frontend = []
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
                    mode, proxied_port, **{aclmode: match})
                sane_match = sanitize(match)
                if any([
                    aclmode == 'wildcard' and match == '*',
                    aclmode == 'regex' and match == '.*'
                ]):
                    aclmode = 'default'
                # in regex mode
                # if obj is string only match on host
                # if ovh is dict
                # try to construct a filter based on
                #   host or url path
                regexes = tuple()
                if aclmode == 'regex':
                    nmatch = {'host': None, 'path': None}
                    if isinstance(match, six.string_types):
                        nmatch['host'] = match
                    elif isinstance(match, list):
                        if len(match) > 0:
                            nmatch['host'] = match[0]
                        if len(match) > 1:
                            nmatch['path'] = match[1]
                    elif isinstance(match, dict):
                        nmatch.update(match)
                    match = nmatch
                    if not (nmatch['host'] or nmatch['path']):
                        raise ValueError(
                            'No host or port in regex haproxy registration')
                    if nmatch['host'] and nmatch['path']:
                        regexes = (
                            ['acl rgx_{sane_match}'
                             ' hdr_reg(host) -i {match[host]}'
                             ' url_reg -i {match[path]}',
                             'acl rgx_{sane_match}port'
                             ' hdr_reg(host) -i {match[host]}:{port}'
                             ' url_reg -i {match[path]}'],
                            ['use_backend {bck_name} if rgx_{sane_match}',
                             'use_backend {bck_name} if rgx_{sane_match}port'])
                    elif nmatch['host']:
                        regexes = (
                            ['acl rgx_{sane_match}'
                             ' hdr_reg(host) -i {match[host]}',
                             'acl rgx_{sane_match}port'
                             ' hdr_reg(host) -i {match[host]}:{port}'],
                            ['use_backend {bck_name} if rgx_{sane_match}',
                             'use_backend {bck_name} if rgx_{sane_match}port'])
                    elif nmatch['path']:
                        regexes = (
                            ['acl rgx_{sane_match}'
                             ' url_reg -i {match[path]}',
                             'acl rgx_{sane_match}port'],
                            [' url_reg -i {match[path]}',
                             'use_backend {bck_name} if rgx_{sane_match}',
                             'use_backend {bck_name} if rgx_{sane_match}port'])
                cfgentries = {
                    'default': (
                        [],
                        ['default_backend {bck_name}']),
                    'regex': regexes,
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
                            port=proxied_port,
                            match=(aclmode == 'wildcard' and
                                   match[2:] or
                                   match),
                            sane_match=sane_match,
                            bck_name=bck_name,
                            bracket='{', ebracket='}')
                        if cfgentry not in opts:
                            opts.append(cfgentry)
    if letsencrypt and not frontend.get('letsencrypt_activated'):
        opts.append('acl letsencrypt'
                    ' path_beg /.well-known/acme-challenge/')
        if has['ssl']:
            letsb = 'bck_letsencrypts'
        else:
            letsb = 'bck_letsencrypt'
        opts.append(
            'use_backend {0} if letsencrypt'.format(letsb))
        frontend['letsencrypt_activated'] = True
    if raw_frontend:
        if isinstance(raw_frontend, six.string_types):
            raw_frontend = [raw_frontend]
        opts.extend(raw_frontend)
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
                                 ssl_check=None,
                                 inter_check=None,
                                 raw_srv=None,
                                 raw_backend=None,
                                 ssl_terminated=None,
                                 http_check=None,
                                 http_fallback_port=None,
                                 http_fallback=None,
                                 letsencrypt=None,
                                 letsencrypt_host=None,
                                 letsencrypt_http_port=None,
                                 letsencrypt_tls_port=None,
                                 ssh_proxy=None,
                                 ssh_proxy_host=None,
                                 ssh_proxy_port=None):
    '''
    Register a specific minion as a backend server
    where haproxy will forward requests to
    '''
    proxied_port = port
    if http_check is None:
        http_check = "OPTIONS /"
    if ssh_proxy:
        proxied_port = port + 1
    if letsencrypt_host is None:
        letsencrypt_host = '127.0.0.1'
    if letsencrypt_http_port is None:
        letsencrypt_http_port = 54080
    if letsencrypt_tls_port is None:
        letsencrypt_tls_port = 54443
    if ssh_proxy is None:
        ssh_proxy = False
    if ssh_proxy_host is None:
        ssh_proxy_host = '127.0.0.1'
    if ssh_proxy_port is None:
        ssh_proxy_port = 22
    # if we proxy some https? traffic, we rely on host to choose a backend
    # and in other cases, we assume to proxy to a TCPs? backend
    if ssl_terminated is None:
        ssl_terminated = False
    if http_fallback is None:
        if not ssl_terminated:
            http_fallback = True
    if raw_backend is None:
        raw_backend = []
    if isinstance(raw_backend, six.string_types):
        raw_backend = [raw_backend]
    if raw_srv is None:
        raw_srv = ''
    ssl_check_forced = isinstance(ssl_check, six.string_types)
    if ssl_check is None:
        ssl_check = 'ssl verify none'
    if inter_check is None:
        inter_check = 'inter 20s'
    if http_fallback_port is None:
        http_fallback_port = 80
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
            servers = []
            if not ssl_terminated:
                servers.append(
                    {'name': 'srv_{0}_ssl'.format(sane_ip),
                     'bind': '{0}:{1}'.format(ip, to_port),
                     'opts': 'check weight 100 {0} {1} {2}'.format(
                         inter_check, ssl_check, raw_srv,
                         bracket='{', ebracket='}')})
            else:
                ssl_check_s = ssl_check_forced and ssl_check or ''
                servers.append(
                    {'name': 'srv_{0}_ssl'.format(sane_ip),
                     'bind': '{0}:{1}'.format(ip, to_port),
                     'opts': 'check weight 100 {0} {1} {2}'.format(
                         inter_check, ssl_check_s, raw_srv)})
            if http_fallback:
                servers.insert(0, {'name': 'srv_{0}_clear'.format(sane_ip),
                                   'bind': '{0}:{1}'.format(
                                       ip, http_fallback_port),
                                   'opts': ('check weight 50'
                                            ' {0} backup {1}').format(
                                                inter_check, raw_srv,
                                                bracket='{', ebracket='}',)})
        else:
            servers = [{'name': 'srv_{0}'.format(sane_ip),
                        'bind': '{0}:{1}'.format(ip, to_port),
                        'opts': 'check {0} {1}'.format(inter_check, raw_srv,
                                                       bracket='{', ebracket='}')}]

    elif mode in [
        'rabbitmq', 'tcp', 'tcps',
        'ssl', 'tls', 'redis', 'redis_auth'
    ]:
        hmode = 'tcp'
        servers = [
               {'name': 'srv_{0}'.format(sane_ip),
                'bind': '{0}:{1}'.format(ip, to_port),
                'opts': 'check {0}'.format(inter_check)}]
    if not hmode.startswith('http'):
        aclmodes = (('default', ['one_backend']),)
    else:
        aclmodes = (('host', hosts),
                    ('regex', regexes),
                    ('wildcard', wildcards))
    if hmode.startswith('http') and letsencrypt:
        backends.update({
            'bck_letsencrypt': {
                'servers': [{
                    'bind': '{0}:{1}'.format(
                        letsencrypt_host, letsencrypt_http_port),
                }]
            },
            'bck_letsencrypts': {
                'servers': [{
                    'bind': '{0}:{1}'.format(
                        letsencrypt_host, letsencrypt_tls_port),
                }]
            }
        })
    if ssh_proxy:
        sshbckname = get_ssh_backend_proxy_name(ssh_proxy_host, ssh_proxy_port,
                                                k='ssh')
        hsshbckname = get_ssh_backend_proxy_name('127.0.0.1', proxied_port,
                                                 k='https')
        backends.update({
            hsshbckname: {
                'mode': 'tcp',
                'servers': [{'bind': '{0}:{1}'.format('127.0.0.1', proxied_port)}],
            },
            sshbckname: {
                'mode': 'tcp',
                'raw_opts': ['option tcplog', 'timeout server 2h'],
                'servers': [{
                    'bind': '{0}:{1}'.format(ssh_proxy_host, ssh_proxy_port)
                }],
            },
        })

    for aclmode, hosts in aclmodes:
        if hosts:
            for match in hosts:
                bck_name = get_backend_name(mode, proxied_port, **{aclmode: match})
                backend = backends.setdefault(bck_name, {})
                backend.setdefault('mode', hmode)
                bopts = backend.setdefault('raw_opts', copy.deepcopy(raw_backend))
                if (bopts or opts) and http_check:
                    bopts.append("option httpchk {0}".format(http_check))
                for o in opts:
                    o = o.format(user=user, password=password, bracket='{', ebracket='}')
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
                http_check = fdata.get('http_check', payload.get('http_check', None))
                regexes = payload.get('regexes', [])
                to_port = int(fdata.get('to_port', port))
                user = fdata.get('user', None)
                password = fdata.get('password', None)
                letsencrypt = fdata.get('letsencrypt', None)
                letsencrypt_host = fdata.get(
                    'letsencrypt_host', None)
                letsencrypt_http_port = fdata.get(
                    'letsencrypt_http_port', None)
                letsencrypt_tls_port = fdata.get(
                    'letsencrypt_tls_port', None)
                ssh_proxy = payload.get('ssh_proxy', None)
                ssh_proxy_host = payload.get('ssh_proxy_host', None)
                ssh_proxy_port = payload.get('ssh_proxy_port', None)
                ssl_terminated = fdata.get('ssl_terminated', None)
                inter_check = fdata.get('inter_check', None)
                raw_backend = fdata.get('raw_backend', None)
                raw_srv = fdata.get('raw_srv', None)
                raw_frontend = fdata.get('raw_frontend', None)
                ssl_check = fdata.get('ssl_check', None)
                http_fallback = fdata.get('http_fallback', None)
                http_fallback_port = fdata.get('http_fallback_port', None)
                mode = fdata.get('mode', proxy_modes.get(sport, 'tcp'))
                frontends = register_frontend(
                    data, port=port, mode=mode, hosts=hosts,
                    frontends=frontends,
                    backends=backends,
                    wildcards=wildcards,
                    regexes=regexes,
                    raw_frontend=raw_frontend,
                    letsencrypt=letsencrypt,
                    ssh_proxy=ssh_proxy,
                    ssh_proxy_host=ssh_proxy_host,
                    ssh_proxy_port=ssh_proxy_port)
                if ssh_proxy:
                    payload.setdefault(
                        'ip', [ssh_proxy_host or '127.0.0.1'])
                if not isinstance(payload['ip'], list):
                    payload['ip'] = payload['ip']
                for ip in payload['ip']:
                    backends = register_servers_to_backends(
                        data,
                        port=port, ip=ip,
                        to_port=to_port, mode=mode,
                        user=user, password=password,
                        hosts=hosts, wildcards=wildcards,
                        regexes=regexes,
                        ssl_terminated=ssl_terminated,
                        inter_check=inter_check,
                        raw_srv=raw_srv,
                        ssl_check=ssl_check,
                        http_check=http_check,
                        http_fallback_port=http_fallback_port,
                        http_fallback=http_fallback,
                        frontends=frontends,
                        backends=backends,
                        raw_backend=raw_backend,
                        letsencrypt=letsencrypt,
                        letsencrypt_host=letsencrypt_host,
                        letsencrypt_http_port=letsencrypt_http_port,
                        letsencrypt_tls_port=letsencrypt_tls_port,
                        ssh_proxy=ssh_proxy,
                        ssh_proxy_host=ssh_proxy_host,
                        ssh_proxy_port=ssh_proxy_port)
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
