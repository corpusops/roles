#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


def copsfburp_get_cname_and_profile(avars, hvars):
    cname = hvars.get('burp_cname', '') or hvars['inventory_hostname']
    profile = avars.get('ansible_virtualization_type', None) in [
        'docker', 'lxc'] and 'vm' or 'baremetal'
    try:
        profile = hvars['burp_client_profile']
    except KeyError:
        try:
            hvars['cops_burpclientserver_profiles_{0}'.format(cname)]
            profile = cname
        except KeyError:
            pass
    return cname, profile


def copsfburp_finish_settings(data, prefixmode, hvars):
    prefixes = {
        'client': 'burp_client_conf_',
        'server': 'burp_client_',
    }
    for k in ['restore_clients', 'custom_lines']:
        val = hvars.get(prefixes[prefixmode]+k, None)
        if val is not None:
            data.update({k: val})
    data.update(hvars.get(prefixes['client']+'extras', {}))
    return data


__funcs__ = {
    'copsfburp_get_cname_and_profile': copsfburp_get_cname_and_profile,
    'copsfburp_finish_settings': copsfburp_finish_settings,
}


class FilterModule(object):

    def filters(self):
        return __funcs__
# vim:set et sts=4 ts=4 tw=80
