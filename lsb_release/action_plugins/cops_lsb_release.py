from __future__ import (absolute_import, division, print_function)

import six
import os
import copy
from os import path, walk
import traceback
import re
import datetime

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.module_utils._text import to_native
from ansible.plugins.action import ActionBase

__metaclass__ = type


class ActionModule(ActionBase):

    lsb_keys = ['description', 'id', 'codename', 'release']

    TRANSFERS_FILES = True

    def get_lsb(self, task_vars):
        '''.'''
        ret = dict([(a, None) for a in self.lsb_keys])
        distribution = task_vars.get('ansible_distribution', None)
        mv = task_vars.get(
            'ansible_distribution_major_version', None)
        v = task_vars.get(
            'ansible_distribution_version', None)
        if mv and not v:
            v = mv
        codename = task_vars.get(
            'ansible_distribution_release', None)
        if distribution:
            ret['id'] = distribution
        if codename:
            ret['codename'] = codename
        if mv:
            ret['release'] = v
        ret['description'] = (
            '{id} {release} ({codename})'.format(**ret))
        return ret

    def run(self, tmp=None, task_vars=None):
        """
        Try to fill lsb variables if not already present
        """
        results = {}
        self._task.args.get('file', '/etc/lsb_release')
        if not task_vars:
            task_vars = {}
        ansible_lsb = task_vars.get('ansible_lsb', {})
        if not ansible_lsb:
            ansible_lsb = {}
        redefine = False
        lsb = {}
        if task_vars['ansible_system'] == 'Linux':
            for k in self.lsb_keys:
                val = ansible_lsb.get(k, None)
                if not val:
                    if not lsb:
                        lsb = self.get_lsb(task_vars)
                    if lsb[k]:
                        ansible_lsb[k] = lsb[k]
                        redefine = True
            if redefine:
                results['ansible_lsb'] = ansible_lsb
        self.show_content = True
        result = {'ansible_facts':  results,
                  '_ansible_no_log': not self.show_content}
        return result
