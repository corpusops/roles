#!/usr/bin/env python
from __future__ import (absolute_import, division, print_function)
# -*- coding: utf-8 -*-

DOCUMENTATION = """
    lookup: cops_net
    author: MakinaCorpus
    version_added: "2.5"
    short_description: wrapper for copsf_burp filters in lookup context
    description:
    - short_description: wrapper for copsf_burp filters in lookup context
    options:
      _terms:
        description: The strings to render
        required: True
      default:
        description:
            - What to return if a variable is undefined.
            - If no default is set, it will result in an error if any of the variables is undefined.
"""

EXAMPLES = """
"""

RETURN = """
_value:
  description:
    - value of the variables requested.
"""

from ansible.errors import AnsibleError, AnsibleUndefinedVariable
from ansible.module_utils.six import string_types
from ansible.plugins.lookup import LookupBase
import six

from copsf_burp import __funcs__


class LookupModule(LookupBase):

    def run(self, terms, variables=None, func='finish_settings', *args, **kwargs):
        if variables is not None:
            self._templar.available_variables = variables

        self.set_options(direct=kwargs)
        default = self.get_option('default')

        ret = []
        kwargs.setdefault('avars', self._templar.available_variables)
        kwargs.setdefault('ansible_vars', self._templar.available_variables)
        for func in terms:
            try:
                ret.append(
                    self._templar.template(
                    self._templar.template(
                        __funcs__['copsfburp_{0}'.format(func)](*args, **kwargs),
                    fail_on_undefined=True))
                )
            except AnsibleUndefinedVariable:
                if default is not None:
                    ret.append(default)
                else:
                    raise

        return ret
# vim:set et sts=4 ts=4 tw=80
