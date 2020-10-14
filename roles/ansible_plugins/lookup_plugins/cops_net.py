from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    lookup: cops_net
    author: kiorky
    version_added: "2.5"
    short_description: wrapper for copsf_net filters in lookup context
    description:
    - short_description: wrapper for copsf_net filters in lookup context
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
from ansible.module_utils import six

from copsf_net import __funcs__
from copsf_api import REGISTRY_DEFAULT_SUFFIX


class LookupModule(LookupBase):

    def run(self, terms, variables=None, func='settings', **kwargs):
        if variables is not None:
            self._templar.available_variables = variables

        self.set_options(direct=kwargs)
        default = self.get_option('default')

        ret = []
        for value in terms:
            try:
                buf = {}
                val = __funcs__['copsnetf_{0}'.format(func)](
                            self._templar.available_variables, value, **kwargs)
                # do not template default registry values !
                for k in [a for a in val if a.endswith(REGISTRY_DEFAULT_SUFFIX)]:
                    buf[k] = val.pop(k)
                self._templar.template(
                    self._templar.template(val, fail_on_undefined=True))
                val.update(buf)
                ret.append(val)
            except AnsibleUndefinedVariable:
                if default is not None:
                    ret.append(default)
                else:
                    raise

        return ret
