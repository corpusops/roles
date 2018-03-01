#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re


def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]


conf_prefix = 'corpusops_ms_iptables_registrations_'
registration_prefix = 'corpusops_ms_iptables_registrations_'


def make_registrations(data, ansible_vars=None):
    '''
    The idea is to have somehow iptables-rules-as-a-service
    where minions register themselves up to the ms_iptables firewall.
    - We search in the variables for any registered frontend
      for each frontend, we try to setup any supported
      ms_iptables configuration knob
    '''
    candidates = sorted(
        [v for v in ansible_vars if (
            v.startswith(registration_prefix))],
        key=natural_sort_key)
    knobs = data['knobs']
    for v in candidates:
        if v == registration_prefix:
            continue
        val = ansible_vars[v]
        # simplified form can be a list of rules -- only
        if isinstance(val, list):
            val = {'rules': val}
        if not isinstance(val, dict):
            continue
        for i, sval in val.items():
            if i not in knobs:
                continue
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
