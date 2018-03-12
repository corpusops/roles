#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import copy
import six
import contextlib
import socket
import re
import json
import urllib2
import os


from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = '''
---
module: corpusops_facts
short_description: get facts for corpusops
'''


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


def ext_ip():
    '''
    Return the external IP address
    '''
    if os.environ.get('CORPUSOPS_SKIP_EXTIP', None):
        return None
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


def main():
    module = AnsibleModule(
        argument_spec=dict(
            ext_ip_value=dict(required=False, default='', type='str'),
            ext_ip=dict(required=False, default=True, type='bool')
        ),
        supports_check_mode=True
    )
    facts = {}
    result = {'ansible_facts': facts}
    if module.params['ext_ip']:
        val = module.params['ext_ip_value']
        if not val:
            val = ext_ip()
        facts.update({'corpusops_facts_ext_ip': val})
    module.exit_json(**result)


if __name__ == '__main__':
    main()
# vim:set et sts=4 ts=4 tw=0: