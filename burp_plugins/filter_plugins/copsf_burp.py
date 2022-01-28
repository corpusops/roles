#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


def copsfburp_get_cname(avars, hvars, *args, **kwargs):
    return hvars.get('burp_cname', '') or hvars['inventory_hostname']


def copsfburp_get_cname_and_profile(avars, hvars, profile_key=None,
                                    *args, **kwargs):
    cname = copsfburp_get_cname(avars, hvars, *args, **kwargs)
    if profile_key is None:
        profile_key = 'burp_client_profile'
    if profile_key in ['burp_clientside_profile']:
        profile = None
    else:
        profile = avars.get('ansible_virtualization_type', None) in [
            'docker', 'lxc', 'container'] and 'vm' or 'baremetal'
    try:
        if profile_key is None:
            raise KeyError('next')
        profile = hvars[profile_key]
    except KeyError:
        try:
            hvars['cops_burpclientserver_profiles_{0}'.format(cname)]
            profile = cname
        except KeyError:
            try:
                avars['cops_burpclientserver_profiles_{0}'.format(cname)]
                profile = cname
            except KeyError:
                pass
    return cname, profile


def copsfburp_finish_settings(data, prefixmode, hvars, *args, **kwargs):
    prefixes = {
        'client': 'burp_client_conf_',
        'server': 'burp_client_',
    }
    for k in ['restore_clients', 'custom_lines']:
        val = hvars.get(prefixes[prefixmode] + k, None)
        if val is not None:
            data.update({k: val})              
    data.update(hvars.get(prefixes['client'] + 'extras', {}))
    return data


__funcs__ = {
    'copsfburp_get_cname': copsfburp_get_cname,
    'copsfburp_get_cname_and_profile': copsfburp_get_cname_and_profile,
    'copsfburp_finish_settings': copsfburp_finish_settings,
}


class FilterModule(object):

    def filters(self):
        return __funcs__
# vim:set et sts=4 ts=4 tw=80
