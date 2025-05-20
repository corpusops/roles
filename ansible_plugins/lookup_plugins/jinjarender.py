from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    lookup: jinjarender
    author: MakinaCorpus
    version_added: "2.5"
    short_description: Template a string without safe/unsafe restrictions
    description:
      - Template a string without safe/unsafe restrictions
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
- name: Show value of 'variablename'
  debug: msg="{{ lookup('vars', 'hostname is {{ansible_fqdn}}')}}"
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


class LookupModule(LookupBase):

    def jrender_seq(self, value):
        ret = []
        for i in value:
            ret.append(self.jrender(i))
        return type(value)(ret)

    def jrender_dict(self, value, failed=None, ret=None):
        if ret is None:
            ret = type(value)()
        oldfailed = []
        if failed is None:
            failed = []
        else:
            oldfailed = failed[:]
        if failed:
            keys = failed
        else:
            keys = [a for a in value]
        for i in keys:
            try:
                ret[i] = self.jrender(value[i])
                if i in failed:
                    failed.pop(failed.index(i))
            except AnsibleUndefinedVariable:
                failed.append(val)

        if failed:
            if (failed == oldfailed):
                raise AnsibleUndefinedVariable(
                    '{0} are not defined'.format(" ".join(failed)))
            else:
                return self.jrender_dict(value, failed=failed, ret=ret)
        return ret

    def jrender(self, value):
        if isinstance(value, (dict,)):
            return self.jrender_dict(value)
        elif isinstance(value, (list, tuple, set)):
            return self.jrender_seq(value)
        else:
            return self._templar.template(value, fail_on_undefined=True)

    def run(self, terms, variables=None, **kwargs):
        if variables is not None:
            self._templar.available_variables = variables

        self.set_options(direct=kwargs)
        default = self.get_option('default')

        ret = []
        for value in terms:
            try:
                ret.append(self.jrender(value))
            except AnsibleUndefinedVariable:
                if default is not None:
                    ret.append(default)
                else:
                    raise

        return ret
