#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import logging
import traceback
import random
import string
import re


from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase


__fn = os.path.abspath(__file__)
__n = os.path.splitext(os.path.basename(__fn))[0]
__mod = os.path.dirname(__fn)
__pmod = os.path.dirname(__mod)
log = logging.getLogger(__n)
__metaclass__ = type
with open(os.path.join(__mod, '../api/cops_load.python')) as fic:
    exec(fic.read(), globals(), locals())

import copsf_api   # noqa
import copsf_json  # noqa


try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()


def cops_get_lock_name(self, variables,
                       registry_name,
                       registry_format,
                       *args, **kwargs):
    lockp = 'localregistry_{0}_{1}'.format(registry_name, registry_format)
    return lockp


def get_path(self, variables,
             name, registry_format='json', *args, **kwargs):
    reg_path = variables.get('corpusops_cfg_path', '~/.corpusops')
    if '{{' in reg_path and '}}' in reg_path:
        reg_path = self._templar.template(reg_path)
    return os.path.expanduser(
        os.path.join(reg_path, "{0}.{1}".format(name, registry_format))
    )


def rand_stored_value(self, variables, key,
                      length=None, force=False, value=None,
                      *args, **kwargs):
    '''
    Generate and store a password.
    At soon as one is stored with a specific key, it will never be renegerated
    unless you set force to true.
    '''
    reg = load(self, variables, 'local_passwords', registry_format='json')
    sav = False
    curval = reg.get(key, None)
    if not curval:
        force = True
    if value is not None:
        curval = value
    elif force:
        curval = copsf_api.rand_value(length=length)
    if reg.get(key, None) != curval:
        reg[key] = curval
        sav = True
    if sav:
        encode(self, variables, 'local_passwords', reg, registry_format='json')
    return reg[key]


def json_dump(self, variables, registry,
              *args, **kwargs):
    content = copsf_json.dump(registry, pretty=True)
    return content


def json_load(self, variables, content,
*args, **kwargs):
    registry = copsf_json.load(content)
    return registry


def load(self, variables, name, registry_format='json',
         *args, **kwargs):
    registry = None
    try:
        with open(
            get_path(self, variables, name, registry_format=registry_format)
        ) as f:
            registry = __funcs__[
                '{0}_load'.format(registry_format)
            ](self, variables, f.read())
    except IOError:
        pass
    if not registry:
        registry = {}
    return registry


def encode(self, variables, name,
           registry, registry_format='json',
           *args, **kwargs):
    lockp = cops_get_lock_name(self, variables, name, registry_format)
    with copsf_api.wait_lock(lockp):
        registryf = get_path(
            self, variables, name, registry_format=registry_format)
        dregistry = os.path.dirname(registryf)
        content = __funcs__[
            '{0}_dump'.format(registry_format)
        ](self, variables, registry)
        sync = False
        if os.path.exists(registryf):
            with open(registryf) as fic:
                old_content = fic.read()
                if old_content != content:
                    sync = True
        else:
            sync = True
        if sync:
            if not os.path.exists(dregistry):
                os.makedirs(dregistry)
            with open(registryf, 'w') as fic:
                fic.write(content)
        os.chmod(registryf, 0700)


__funcs__ = {
    'json_dump': json_dump,
    'json_load': json_load,
    'registry_load': load,
    'registry_encode': encode,
    'rand_stored_value': rand_stored_value,
}


class LookupModule(LookupBase):

    def run(self, actions, variables=None, inject=None, *args, **kwargs):
        rets = []
        try:
            for action in actions:
                func, fargs, fkwargs = action[0], tuple(), {}
                if len(action) > 1:
                    fargs = action[1]
                if len(action) > 2:
                    fkwargs = action[2]
                rets.append(
                    __funcs__[func](self, variables, *fargs, **fkwargs))
        except Exception, exc:
            trace = traceback.format_exc()
            display.v(trace)
            raise(exc)
        return rets
        # display.debug("File lookup term: %s" % term)
        # display.vvvv(u"File lookup using %s as file" % lookupfile)
        # raise AnsibleParserError()
# vim:set et sts=4 ts=4 tw=80:
