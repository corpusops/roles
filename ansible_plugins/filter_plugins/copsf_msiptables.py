#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re
import copy


def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]


conf_prefix = 'corpusops_ms_iptables_registrations_'
registration_prefix = 'registrations_'


def make_registrations(data, ansible_vars=None):
    '''
    The idea is to have somehow iptables-rules-as-a-service
    where minions register themselves up to the ms_iptables firewall.
    - We search in the variables for any registered frontend
      for each frontend, we try to setup any supported
      ms_iptables configuration knob
    '''
    candidates = sorted(
        [v for v in data if (
            v.startswith(registration_prefix))],
        key=natural_sort_key)
    knobs = data['knobs']
    load_registrations = ansible_vars.get(
        '_corpusops_ms_iptables_registrations', {}
    ).get('load_registrations',
          ansible_vars.get(
              'corpusops_ms_iptables_registrations_load_registrations', True))
    if not load_registrations:
        return data
    for v in candidates:
        if v in [registration_prefix,
                 registration_prefix+'vars']:
            continue
        val = data[v]
        # simplified form can be a list of rules -- only
        if isinstance(val, list):
            val = {'rules': val}
        if not isinstance(val, dict):
            continue
        for i, sval in val.items():
            if i not in knobs:
                continue
            sval = copy.deepcopy(sval)
            try:
                oval = data[i]
                if isinstance(oval, list) and isinstance(sval, list):
                    oval.extend(sval)
                    sval = oval
                data[i] = sval
            except KeyError:
                data[i] = sval
    return data


__funcs__ = {
    'copsmsiptablesf_make_registrations': make_registrations,
}


class FilterModule(object):

    def filters(self):
        return __funcs__
# vim:set et sts=4 ts=4 tw=80
