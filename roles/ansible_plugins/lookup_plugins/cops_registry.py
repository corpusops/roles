from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    lookup: cops_registry
    author: kiorky
    version_added: "2.5"
    short_description: Assemble vars under a common prefix under a namespaced dict of those vars
    description:
    - Assemble vars under a common prefix under a namespaced dict of those vars
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
  debug: msg="{{ lookup('vars', 'common_prefix_')}}
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
import logging
import traceback

from collections import OrderedDict
from copsf_api import __funcs__, REGISTRY_DEFAULT_SUFFIX


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        log = logging.getLogger('corpusops.lookup.cops_registry')
        if variables is not None:
            self._templar.available_variables = variables

        self.set_options(direct=kwargs)
        default = self.get_option('default')
        gs = kwargs.get('global_scope', True)
        kwargs['global_scope'] = False

        ret = []
        for value in terms:
            try:
                # try to resolve the overrides dict if it comes from 
                # recent ansible versions and a form like:
                # - include_role: {name: corpusops/registry}
                #   loop: "{{myvar}}" /
                #   vars: 
                #      cops_vars_registry_target: foo
                #      _foo: "{{myvar.subelement}}"
                overrides_prefix = '_{0}'.format(value[:-1])
                ov = self._templar.available_variables.get(overrides_prefix, None)
                if ( 
                    ov and 
                    isinstance(ov, six.string_types) and
                    '{{' in ov and
                    '}}' in ov and
                    '\n' not in ov
                ):
                    try:
                        ovr = self._templar.template(ov)
                        if isinstance(ovr, dict):
                            self._templar.available_variables.update(
                                {overrides_prefix: ovr})
                    except Exception:
                        trace = traceback.format_exc()
                        log.error('failed to render registry overrides: {0}'.format(value))
                        log.error(trace)
                val = __funcs__['copsf_registry'](
                    self._templar.available_variables, value, **kwargs)
                registry = self._templar.template(self._templar.template(val[0], fail_on_undefined=True))
                defaults_vals_reg ='__{0}{1}'.format(value, REGISTRY_DEFAULT_SUFFIX)
                rval = OrderedDict()
                if gs:
                    rval[defaults_vals_reg] = val[1].get(defaults_vals_reg)
                    for v, ival in six.iteritems(registry):
                        rval['{0}{1}'.format(value, v)] = ival
                    rval['{0}vars'.format(value)] = registry
                else:
                    rval = registry
                ret.append(rval)
            except AnsibleUndefinedVariable:
                if default is not None:
                    ret.append(default)
                else:
                    raise

        return ret
