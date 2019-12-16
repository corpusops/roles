#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import copy
import ipaddr
import six
import contextlib
import socket
import re
import urllib2

from distutils.version import LooseVersion


try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
try:
    import Crypto.Random  # pylint: disable=E0611
    HAS_RANDOM = True
except ImportError:
    HAS_RANDOM = False


def is_valid_v6(ip_or_name):
    valid = False
    familly = socket.AF_INET6
    if not valid:
        try:
            if socket.inet_pton(familly, ip_or_name):
                return True
        except Exception:
            pass
    return valid


def is_valid_v4(ip_or_name):
    valid = False
    familly = socket.AF_INET
    if not valid:
        try:
            if socket.inet_pton(familly, ip_or_name):
                return True
        except Exception:
            pass
    return valid


def is_valid_ip(ip_or_name):
    valid = False
    for func in [is_valid_v6, is_valid_v4]:
        valid = func(ip_or_name)
        if valid:
            break
    return valid


def is_ip(ip):
    return is_valid_ip(ip)


def ext_ip(ansible_vars):
    '''
    Return the external IP address
    '''
    ext_ip = ansible_vars.get(
        'corpusops_network_live_ext_ip_value', None)
    if not ansible_vars.get(
        'corpusops_network_get_ext_ip', False
    ):
        return ext_ip
    check_ips = ('http://ipecho.net/plain',
                 'http://v4.ident.me')

    for url in check_ips:
        try:
            with contextlib.closing(urllib2.urlopen(url, timeout=3)) as req:
                ip_ = req.read().strip()
                if not is_valid_v4(ip_):
                    continue
            return ip_
        except (urllib2.HTTPError, urllib2.URLError, socket.timeout):
            continue
    return ext_ip


def is_loopback(ip):
    try:
        iaddr = ipaddr.IPAddress(ip)
        return iaddr.is_loopback
    except (Exception,):
        return False


def is_link_local(ip):
    try:
        iaddr = ipaddr.IPAddress(ip)
        return iaddr.is_link_local
    except (Exception,):
        return False


def is_public(ip):
    try:
        iaddr = ipaddr.IPAddress(ip)
        return (
            not iaddr.is_private and
            not iaddr.is_reserved and
            not iaddr.is_link_local and
            not iaddr.is_loopback)
    except (Exception,):
        return True


def get_ifc_ip_addrs(ifacescol, ifc):
    ips = []
    ip6s = []
    idata = ifacescol.get(ifc, {})
    ips.append(idata.get('ipv4', {}).get('address'))
    for sdata in idata.get('ipv4_secondaries', []):
        ips.append(sdata.get('address'))
    for sdata in idata.get('ipv6', []):
        ip6s.append(sdata.get('address'))
    ips = [i for i in ips if i]
    ip6s = [i for i in ip6s if i]
    return ips, ip6s


def default_net(ansible_vars):
    '''
    Function to be used on a running system
    (opposed to settings)
    Use by default a bridge with main interface as first port
    or the main interface as the link with internet
    '''
    all_ifaces = dict([
        (a, ansible_vars.get('ansible_{0}'.format(a), {}))
        for a in ansible_vars.get('ansible_interfaces', [])])
    default_if_data = ansible_vars.get('ansible_default_ipv4', {})
    default_if = default_if_data['interface']
    default_ip = default_if_data.get('address', None)
    default_route = default_if_data.get('gateway', None)
    # default mode: masquerading on the interface containing
    # the default route for lxc and docker containers
    # later, we will add maybe support for failover ip bridges/ vmac
    real_ifaces = dict([a for a in six.iteritems(all_ifaces)
                        if a[1].get('type', None) == 'ether' and
                        'veth' not in a[0]])
    bridge_ifaces = dict([a for a in six.iteritems(all_ifaces)
                          if a[1].get('type', None) == 'bridge'])
    v4addr = mainip(ansible_vars)
    # if a bridge has the if port, use that instead
    if bridge_ifaces and not v4addr:
        for br, brdata in six.iteritems(bridge_ifaces):
            ifs = brdata.get('interfaces', [])
            if default_if in ifs:
                default_if = br
                break
    try:
        default_net_ = ''
        if default_ip:
            default_net_ = get_netmask(default_ip)
        parts = default_net_.split('.')
        parts.reverse()
        default_netmask = 32
        for part in parts:
            if part == '0':
                default_netmask -= 8
            else:
                break
    except Exception:
        default_net_ = None
        default_netmask = 32

    return {'default_route': default_route,
            'default_net': default_net_,
            'default_netmask': default_netmask,
            'all_ifaces': dict([
                (a, get_ifc_ip_addrs(all_ifaces, a))
                for a in all_ifaces]),
            'real_ifaces': dict([
                (a, get_ifc_ip_addrs(real_ifaces, a))
                for a in real_ifaces]),
            'bridge_ifaces':   dict([
                (a, get_ifc_ip_addrs(bridge_ifaces, a))
                for a in bridge_ifaces]),
            'default_if': default_if}


def get_fo_netmask(dn, ip):
    '''Get netmask for an ip failover
    '''
    netmask = '255.255.255.255'
    return netmask


def get_fo_broadcast(dn, ip):
    '''Get broadcast for an ip failover
    '''
    broadcast = ip
    return broadcast


def sort_ifaces(infos):
    a = infos[0]
    key = a
    if re.match('^(eth0)', key):
        key = '100___' + a
    if re.match('^(eth[123456789][0123456789]+\|em|wlan)', key):
        key = '200___' + a
    if re.match('^(lxc\|docker)', key):
        key = '300___' + a
    if re.match('^(veth\|lo)', key):
        key = '900___' + a
    return key


def get_netmask(ip, num='0'):
    '''Get a server broadcase
    ipsubnet.0
    '''
    gw = '.'.join(ip.split('.')[:-1] + [num])
    return gw


def get_broadcast(ip, num='255'):
    '''Get a server broadcase
    ipsubnet.255
    '''
    num = '255'
    gw = '.'.join(ip.split('.')[:-1] + [num])
    return gw


def get_domain(ansible_vars, fqdn=None):
    if not fqdn:
        fqdn = ansible_vars['ansible_fqdn']
    domain_parts = fqdn.split('.')
    return '.'.join(domain_parts[1:])


def get_hostname(ansible_vars, full=False):
    hostname = ansible_vars['ansible_fqdn']
    if not full:
        hostname = hostname.split('.')[0]
    return hostname


def mainip6(ansible_vars):
    return ansible_vars.get('ansible_default_ipv6', {}).get(
        'address', None)


def mainip(ansible_vars):
    return ansible_vars.get('ansible_default_ipv4', {}).get(
        'address', None)


def have_lxc_if(ansible_vars):
    ret = None
    data_net = default_net(ansible_vars)
    all_ifaces = data_net['all_ifaces']
    if True in ['lxc' in a[0] for a in all_ifaces]:
        ret = False
    return ret


def have_vpn_if(ansible_vars):
    ret = None
    data_net = default_net(ansible_vars)
    all_ifaces = data_net['all_ifaces']
    if True in [a[0].startswith('tun') for a in all_ifaces]:
        ret = True
    return ret


def have_docker_if(ansible_vars):
    ret = None
    data_net = default_net(ansible_vars)
    all_ifaces = data_net['all_ifaces']
    if True in ['docker' in a[0] for a in all_ifaces]:
        ret = True
    return ret


def append_netmask(ip):
    # ipv6 is not supported at the moment
    if ':' in ip:
        return ip
    else:
        chunks = ip.split('.')[:4]
        if len(chunks) < 4:
            while len(chunks[:]) < 4:
                chunks.append('0')
        netm = 32
        if chunks[-1] in ['0', 0]:
            for i in range(4):
                if chunks[4 - (i+1)] in ['0']:
                    netm -= 8
                else:
                    break
            if ip.startswith('172.16'):
                netm = '12'
        netm = "{0}".format(netm)
        net = '.'.join(chunks) + '/' + netm
        return net


def live_settings(ansible_vars, prefix):
    '''
    network registry
    '''
    import copsf_api as api
    netdata, _ = api.copsf_registry(
        ansible_vars=ansible_vars, prefix=prefix,
        global_scope=False)
    # _ = [netdata.pop(i, None)  # noqa
    #      for i in [a for a in netdata]
    #      if i.startswith('live_')]
    return netdata


def settings(ansible_vars, live_prefix, prefix):
    '''
    network registry
    '''
    import copsf_api as api
    live = ansible_vars[live_prefix+'vars']
    netdata, _ = api.copsf_registry(
        ansible_vars=ansible_vars, prefix=prefix,
        global_scope=False)
    rp = netdata['reverse_proxy']
    if rp['is_proxified'] is None:
        cvars = ansible_vars['corpusops_vars']
        if (
            cvars['is_vagrant'] or
            cvars['is_lxc'] or
            cvars['is_docker'] or
            cvars['is_container']
        ):
            rp['is_proxified'] = True
    if rp['is_proxified']:
        if not rp['do_not_add_gw']:
            rips = [live['mainip'], live['net']['default_route']]
            _ = [netdata['reverse_proxy_addresses'].append(i)  # noqa
                 for i in rips
                 if i not in netdata['reverse_proxy_addresses']]
    for imapping in netdata['ointerfaces']:
        for ikey, idata in imapping.items():
            ifname = idata.get('ifname', ikey)
            iconf = netdata['interfaces'].setdefault(ifname, {})
            iconf.update(idata)
    for ifc, data in netdata['interfaces'].items():
        data.setdefault('ifname', ifc)
    # Automatic order of network interfaces
    # (done if we did not have explicitly overriden it)
    # configure alias interfaces only after real ones...
    if not netdata['configuration_order']:
        iorder = netdata['configuration_order']
        for line in netdata['ointerfaces']:
            iorder += [ifc for ifc, ifcdata in six.iteritems(line)
                       if ':' not in ifc]
            iorder += [ifc for ifc, ifcdata in six.iteritems(line)
                       if ':' in ifc]
        iorder += [a for a in netdata['interfaces'] if ':' not in a]
        iorder += [a for a in netdata['interfaces'] if ':' in a]
        netdata['configuration_order'] = api.uniquify(iorder)
    return netdata


__funcs__ = {
    'copsnetf_default_net': default_net,
    'copsnetf_ext_ip': ext_ip,
    'copsnetf_get_broadcast': get_broadcast,
    'copsnetf_get_fo_broadcast': get_fo_broadcast,
    'copsnetf_get_fo_netmask': get_fo_netmask,
    'copsnetf_get_netmask': get_netmask,
    'copsnetf_have_docker_if': have_docker_if,
    'copsnetf_have_lxc_if': have_lxc_if,
    'copsnetf_have_vpn_if': have_vpn_if,
    'copsnetf_domain': get_domain,
    'copsnetf_hostname': get_hostname,
    'copsnetf_is_ip': is_ip,
    'copsnetf_is_link_local': is_link_local,
    'copsnetf_is_loopback': is_loopback,
    'copsnetf_is_public': is_public,
    'copsnetf_is_valid_ip': is_valid_ip,
    'copsnetf_is_valid_v4': is_valid_v4,
    'copsnetf_is_valid_v4': is_valid_v4,
    'copsnetf_mainip': mainip,
    'copsnetf_mainip6': mainip6,
    'copsnetf_settings': settings,
    'copsnetf_live_settings': live_settings,
    'copsnetf_get_ifc_ip_addrs': get_ifc_ip_addrs,
}


class FilterModule(object):

    def filters(self):
        return __funcs__
# vim:set et sts=4 ts=4 tw=80
