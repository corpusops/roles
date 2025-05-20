from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    lookup: cops_mysql
    author: MakinaCorpus
    version_added: "2.5"
    short_description: wrapper for copsf_mysql filter in lookup context
    description:
    - wrapper for copsf_mysql filter in lookup context
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

from copsf_mysql import __funcs__


class LookupModule(LookupBase):

    def run(self, terms, variables=None, func='copsf_mysql', **kwargs):
        if variables is not None:
            self._templar.available_variables = variables

        self.set_options(direct=kwargs)
        default = self.get_option('default')

        ret = []
        for value in terms:
            try:
                pass1, _ = __funcs__['{0}'.format(func)](
                    prefix=value,
                    ansible_vars=self._templar.available_variables, **kwargs)
                pass2 = self._templar.template(pass1, fail_on_undefined=True)
                ret.append(self._templar.template(pass2))
            except AnsibleUndefinedVariable:
                if default is not None:
                    ret.append(default)
                else:
                    raise

        return ret

# vim:set et sts=4 ts=4 tw=80
