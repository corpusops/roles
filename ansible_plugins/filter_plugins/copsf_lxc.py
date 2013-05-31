#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from ansible.module_utils import six
import logging

__fn = os.path.abspath(__file__)
__n = os.path.splitext(os.path.basename(__fn))[0]
__mod = os.path.dirname(__fn)
__pmod = os.path.dirname(__mod)
log = logging.getLogger(__n)
__metaclass__ = type
with open(os.path.join(__mod, '../api/cops_load.python')) as fic:
    exec(fic.read(), globals(), locals())


def ssh_connection_proxy(_, inventory_hostname, hostvars, *args, **kwargs):
    try:
        hvars = hostvars[inventory_hostname]
    except KeyError:
        hvars = {}
    user = hvars.get(
        'ansible_user', 'root')
    gw = hvars.get(
        'ansible_fqdn', inventory_hostname)
    gw_port = hvars.get('ansible_port', None)
    if (
        (hvars.get('ansible_connection', '')
         in ['local']) or (
            inventory_hostname in ['localhost', 'ip6-localhost',
                                   '127.0.0.1', '127.0.1.1', '::1']
         )

    ):
        val = ''
    else:
        val = ("-o ProxyCommand=\""
               "ssh -W %h:%p -q {user}@{gw}").format(
                   user=user, gw=gw)
        if gw_port:
            val += " -p {0}".format(gw_port)
        val += "\""
    return val


def nulval(val):
    if val == '-':
        val = None
    return val


def copsf_lxc_subnet(ip, cidr=True):
    res = '24'
    if ip.startswith('10.'):
        res = '16'
    if not cidr:
        res = {'24': '255.255.255.0'}.get(res, '255.255.0.0')
    return res


def lxcls_mangle(val, restrict_to=None, *args, **kwargs):
    if isinstance(restrict_to, six.string_types):
        restrict_to = restrict_to.split(',')
    if restrict_to and not isinstance(restrict_to, (tuple, list, dict)):
        restrict_to = None
    lxcs = {}
    for line in val['stdout_lines']:
        sparts = [a.strip() for a in line.split()]
        cname = sparts[0]
        if restrict_to and (cname not in restrict_to):
            continue
        container = lxcs.setdefault(cname, {})
        container.update({
          'state': sparts[1],
          'ipv4': nulval(sparts[4]),
          'ipv6': nulval(sparts[5]),
          'autostart': nulval(sparts[2]),
          'groups': nulval(sparts[3]),
         })
    return lxcs


__funcs__ = {
    'lxc_lxcls_mangle': lxcls_mangle,
    'lxc_ssh_connection_proxy': ssh_connection_proxy,
    'copsf_lxc_lxcls_mangle': lxcls_mangle,
    'copsf_lxc_ssh_connection_proxy': ssh_connection_proxy,
    'copsf_lxc_subnet': copsf_lxc_subnet,
}


class FilterModule(object):
    ''' Ansible core jinja2 filters '''

    def filters(self):
        return __funcs__
# vim:set et sts=4 ts=4 tw=80:
