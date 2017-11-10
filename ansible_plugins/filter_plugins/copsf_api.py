#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import six
import time
import collections
import os
import contextlib
import hashlib
import logging
import fcntl
import copy
import tempfile
import random
import string
import re
from distutils.version import LooseVersion


try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
try:
    import Crypto.Random  # pylint: disable=E0611
    HAS_RANDOM = True
except ImportError:
    HAS_RANDOM = False


is_really_a_var = re.compile('(\{[^:}]+\})', re.M | re.U)
__fn = os.path.abspath(__file__)
__n = os.path.splitext(os.path.basename(__fn))[0]
__mod = os.path.dirname(__fn)
__pmod = os.path.dirname(__mod)
log = logging.getLogger(__n)
__metaclass__ = type
_DEFAULT = object()
SUBREGISTRIES_KEYS = 'cops_sub_namespaces'
REGISTRY_DEFAULT_SUFFIX = '_REGISTRY_DEFAULT'
REGISTRY_DEFAULT_VALUE = '_CORPUSOPS_DEFAULT_VALUE'
with open(os.path.join(__mod, '../api/cops_load.python')) as fic:
    exec(fic.read(), globals(), locals())


class LockError(Exception):
    '''.'''


def lock(fd, flags=fcntl.LOCK_NB | fcntl.LOCK_EX):
    fcntl.flock(fd.fileno(), flags)


def unlock(fd):
    fcntl.flock(fd.fileno(), fcntl.LOCK_UN)


def splitstrip(a):
    res = a
    if isinstance(a, six.string_types):
        a = a.split()
    if isinstance(a, list):
        res = []
        for b in a:
            if isinstance(b, six.string_types):
                b = b.strip()
                res.append(b)
    return res


def dictupdate(dest, upd, recursive_update=True):
    '''
    Recursive version of the default dict.update
    Merges upd recursively into dest
    But instead of merging lists, it overrides them from target dict
    '''
    if (not isinstance(dest, collections.Mapping)) \
            or (not isinstance(upd, collections.Mapping)):
        msg = ('Cannot update using non-dict types'
               ' in dictupdate.update()')
        try:
            msg = "{0}\ndest: {1}\nupd: {2}".format(msg, dest, upd)
        except Exception:
            try:
                msg = "{0}\ndest: {1}".format(msg, dest, upd)
            except Exception:
                msg = "{1}\nupd: {2}".format(msg, dest, upd)
        raise TypeError(msg)
    updkeys = list(upd.keys())
    if not set(list(dest.keys())) & set(updkeys):
        recursive_update = False
    if recursive_update:
        for key in updkeys:
            val = upd[key]
            try:
                dest_subkey = dest.get(key, None)
            except AttributeError:
                dest_subkey = None
            if isinstance(dest_subkey, collections.Mapping) \
                    and isinstance(val, collections.Mapping):
                ret = dictupdate(dest_subkey, val)
                dest[key] = ret
            else:
                dest[key] = upd[key]
        return dest
    else:
        try:
            dest.update(upd)
        except AttributeError:
            # this mapping is not a dict
            for k in upd:
                dest[k] = upd[k]
        return dest

@contextlib.contextmanager  # noqa
def wait_lock(
    lockp='lock',
    wait_timeout=60,
    logger=None,
    error_msg='Another instance is locking {lock}'
):
    old_runt = runt = now = time.time()
    end = now + wait_timeout
    if logger is None:
        logger = log
    if os.path.sep not in lockp:
        lockp = os.path.join(
            tempfile.gettempdir(),
            'corpusops_lock_{0}'.format(lockp))
    locko = None
    for i in range(10):
        try:
            if not os.path.exists(lockp):
                with open(lockp, 'w') as fic:
                    fic.write('')
            locko = open(lockp)
        except (IOError, OSError):
            time.sleep(0.5)
    if locko is None:
        raise LockError(
            'Could not get a file in {lock}'.format(lock=lockp))
    has_lock = False
    while time.time() < end:
        try:
            lock(locko)
            has_lock = True
            break
        except IOError:
            if runt - old_runt > 4:
                old_runt = runt
                logger.warn('Locked: {0} wait'.format(lockp))
            runt = time.time()
            time.sleep(0.5)
    if not has_lock:
        raise LockError(error_msg.format(lock=lockp))
    yield
    try:
        if os.path.exists(lockp):
            os.unlink(lockp)
    except (OSError, IOError):
        pass
    try:
        unlock(locko)
    except (OSError, IOError):
        pass


def dirname(sstring, level=-1):
    if sstring.endswith('/'):
        sstring = sstring[:-1]
    return os.path.dirname(sstring)


def basename(sstring, level=None):
    if sstring.endswith(os.path.sep):
        sstring = sstring[:-1]
    if level:
        sstring = os.path.sep.join(
            sstring.split(os.path.sep)[:level])
    return os.path.basename(sstring)


def secure_password(length=None, use_random=True, choices=None,
                    *args, **kwargs):
    '''
    Generate a secure password.
    '''
    if not length:
        length = 16
    length = int(length)
    pw = ''
    if not choices:
        choices = string.ascii_letters + string.digits
    while len(pw) < length:
        if HAS_RANDOM and use_random:
            c = re.sub(r'\W', '', Crypto.Random.get_random_bytes(1))
            try:
                if c in choices:
                    pw += c
            except Exception:
                pass
        else:
            pw += random.SystemRandom().choice(choices)
    return pw


def rand_value(*args, **kwargs):
    length = kwargs.get('length', None)
    return secure_password(length=length)


def hash_value(sstring, typ='md5', func='hexdigest'):
    '''
    Return the hash of a string::

        cops_hash foo
        cops_hash foo md5
        cops_hash foo sha1
        cops_hash foo sha224
        cops_hash foo sha256
        cops_hash foo sha384
        cops_hash foo sha512
    '''
    if func not in ['hexdigest', 'digest']:
        func = 'hexdigest'

    if typ not in [
        'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512'
    ]:
        raise TypeError('{0} is not valid hash'.format(typ))
    return getattr(getattr(hashlib, typ)(sstring), func)()


def is_typ_(val, typs_):
    if not isinstance(typs_, (list, tuple, set)):
        typs_ = [typs_]
    test1 = type(val) in typs_
    if not test1:
        try:
            return isinstance(val, typs_)
        except Exception:
            return False


def go_pdb(val=None, *args,  **kwargs):
    from pdb_clone import pdb as pdbc
    pdbc.set_trace_remote()
    return val


def copsf_bool(value, asbool=True):
    if isinstance(string, six.string_types):
        if value and asbool:
            low = value.lower().strip()
            if low in [
                'non', 'no', 'n', 'off', '0',
            ]:
                return False
            if low in [
                'oui', 'yes', 'y', 'on', '1',
            ]:
                return True
    return bool(value)


def cops_deepcopy(val):
    return copy.deepcopy(val)


def cops_copy(val):
    return copy.copy(val)


def looseversion(v):
    return LooseVersion(v)


def unresolved(data):
    ret = None
    if isinstance(data, six.string_types):
        if '{' in data and '}' in data:
            if is_really_a_var.search(data):
                ret = True
            else:
                ret = False
        else:
            ret = False
    elif isinstance(data, dict):
        for k, val in six.iteritems(data):
            ret1 = unresolved(k)
            ret2 = unresolved(val)
            ret = ret1 or ret2
            if ret:
                break
    elif isinstance(data, (list, set)):
        for val in data:
            ret = unresolved(val)
            if ret:
                break
    return ret


def _str_resolve(new, original_dict=None, this_call=0, topdb=False):

    '''
    low level and optimized call to format_resolve
    '''
    init_new = new
    # do not directly call format to handle keyerror in original mapping
    # where we may have yet keyerrors
    if isinstance(original_dict, dict):
        for k in original_dict:
            reprk = k
            if not isinstance(reprk, six.string_types):
                reprk = '{0}'.format(k)
            subst = '{' + reprk + '}'
            if subst in new:
                subst_val = original_dict[k]
                if isinstance(subst_val, (list, dict)):
                    inner_new = format_resolve(
                        subst_val, original_dict,
                        this_call=this_call, topdb=topdb)
                    # composed, we take the repr
                    if new != subst:
                        new = new.replace(subst, str(inner_new))
                    # no composed value, take the original list
                    else:
                        new = inner_new
                else:
                    if new != subst_val:
                        new = new.replace(subst, str(subst_val))
            if not unresolved(new):
                # new value has been totally resolved
                break
    return new, new != init_new


def str_resolve(new, original_dict=None, this_call=0, topdb=False):
    return _str_resolve(
        new, original_dict=original_dict, this_call=this_call, topdb=topdb)[0]


def _format_resolve(value,
                    original_dict=None,
                    this_call=0,
                    topdb=False,
                    retry=None,
                    **kwargs):
    '''
    low level and optimized call to format_resolve
    '''
    if not original_dict:
        original_dict = OrderedDict()

    if this_call == 0:
        if not original_dict and isinstance(value, dict):
            original_dict = value

    changed = False

    if kwargs:
        original_dict.update(kwargs)

    if not unresolved(value):
        return value, False

    if isinstance(value, dict):
        new = type(value)()
        for key, v in value.items():
            val, changed_ = _format_resolve(v, original_dict, topdb=topdb)
            if changed_:
                changed = changed_
            new[key] = val
    elif isinstance(value, (list, tuple)):
        new = type(value)()
        for v in value:
            val, changed_ = _format_resolve(v, original_dict, topdb=topdb)
            if changed_:
                changed = changed_
            new = new + type(value)([val])
    elif isinstance(value, six.string_types):
        new, changed_ = _str_resolve(value, original_dict, topdb=topdb)
        if changed_:
            changed = changed_
    else:
        new = value

    if retry is None:
        retry = unresolved(new)

    while retry and (this_call < 100):
        new, changed = _format_resolve(new,
                                       original_dict,
                                       this_call=this_call,
                                       retry=False,
                                       topdb=topdb)
        if not changed:
            retry = False
        this_call += 1
    return new, changed


def format_resolve(value,
                   original_dict=None,
                   this_call=0, topdb=False, **kwargs):

    '''
    Resolve a dict of formatted strings, mappings & list to a valued dict
    Please also read the associated test::
        {"a": ["{b}", "{c}", "{e}"],
         "b": 1,
         "c": "{d}",
         "d": "{b}",
         "e": "{d}",
        }
        ====>
        {"a": ["1", "1", "{e}"],
         "b": 1,
         "c": "{d}",
         "d": "{b}",
         "e": "{d}",
        }
    '''
    return _format_resolve(value,
                           original_dict=original_dict,
                           this_call=this_call,
                           topdb=topdb,
                           **kwargs)[0]


copsf_format_resolve = format_resolve


def copsf_to_lower(val):
    if isinstance(val, six.string_types):
        val = val.lower()
    elif isinstance(val, dict):
        val = type(val)()
        for i in [a for a in val]:
            val[i] = copsf_to_lower(val[i])
    elif isinstance(val, list):
        val = type(val)()
        for i in range(len(val)):
            val.append(copsf_to_lower(val[i]))
    return val


def copsf_format_val(val, ansible_vars):
    if isinstance(val, six.string_types):
        val = val.format(**ansible_vars)
        return val
    elif isinstance(val, dict):
        nval = type(val)()
        for i in [a for a in val]:
            nval[i] = copsf_format_val(val[i], ansible_vars)
        return nval
    elif isinstance(val, list):
        nval = type(val)()
        for i in range(len(val)):
            nval.append(copsf_format_val(val[i], ansible_vars))
        return nval
    else:
        return val


def copsf_compute_lower(ansible_vars, namespaced, lowered):
    for k in lowered:
        if k not in namespaced:
            continue
        val = copsf_to_lower(namespaced[k])
        namespaced[k] = val
    return namespaced


def copsf_compute_defaults(ansible_vars, namespaced, computed_defaults):
    for k in computed_defaults:
        if k not in namespaced:
            continue
        val = copsf_format_val(namespaced[k], ansible_vars)
        namespaced[k] = val
    return namespaced


def get_name_prefix(name_prefix, prefix, suffix='vars'):
    if not name_prefix:
        name_prefix = prefix + suffix
    return name_prefix


def copsf_reset_vars_from_registry(ansible_vars,
                                   prefix, registry_suffix=REGISTRY_DEFAULT_SUFFIX):  #noqa
    dsvars = ansible_vars.setdefault('__'+prefix+registry_suffix, {})
    for dsvar in [a for a in dsvars]:
        data = dsvars.pop(dsvar, {})
        val = data['value']
        svar = data['variable']
        if val == REGISTRY_DEFAULT_VALUE:
            continue
        ansible_vars[svar] = val
    return ansible_vars


def copsf_registry_to_vars(namespaced,
                           ansible_vars,
                           prefix,
                           global_scope=False,
                           name_prefix=None,
                           registry_suffix=REGISTRY_DEFAULT_SUFFIX):
    name_prefix = get_name_prefix(name_prefix, prefix)
    scope = {}
    scope.update({name_prefix: namespaced})
    sdvars = '__'+prefix+registry_suffix
    default_vars = ansible_vars.setdefault(sdvars, {})
    for k in [a for a in namespaced]:
        svar = prefix + k
        dsvar = svar + registry_suffix
        default_vars.setdefault(dsvar, {
            'value': ansible_vars.get(svar, REGISTRY_DEFAULT_VALUE),
            'variable': svar})
        scope[svar] = namespaced[k]
    scope[sdvars] = default_vars
    ansible_vars.update(scope)
    if not global_scope:
        scope = namespaced
    return scope, ansible_vars


def copsf_knobs(ansible_vars, namespaced, knobs, flavors=None):
    """
    Per os knobs to filter variables and prepare registry adapting to
    the environment target OS
    """
    if not flavors:
        flavors = []
    if flavors:
        for v in knobs:
            if namespaced.get(v, None) is not None:
                continue
            for flav in flavors:
                if (
                    flav == 'default' or
                    ansible_vars['ansible_os_family'].lower() == flav or
                    ansible_vars['ansible_lsb']['id'].lower() == flav
                ):
                    os_vpref = v + '_' + flav
                    if os_vpref in namespaced:
                        namespaced.update({v: namespaced[os_vpref]})
                        break
    return namespaced


def copsf_load_registry_overrides(ansible_vars,
                                  prefix,
                                  registry=None,
                                  overrides_prefix=None):
    if overrides_prefix is None and prefix:
        overrides_prefix = '_{0}'.format(prefix[:-1])
    overrides = ansible_vars.get(overrides_prefix, {})
    registry = registry or ansible_vars.get(prefix, {})
    if (
        isinstance(overrides, dict) and
        isinstance(registry, dict)
    ):
        registry.update(overrides)
    return registry


def copsf_to_namespace(ansible_vars,
                       prefix,
                       do_load_overrides=None,
                       overrides_prefix=None,
                       sub_namespaced=None,
                       flavors=None,
                       name_prefix=None,
                       namespaced=None,
                       knobs=None,
                       lowered=None,
                       computed_defaults=None,
                       subos_append=None,
                       prefixes=None,
                       sub_registries_key=SUBREGISTRIES_KEYS,
                       registry_suffix=REGISTRY_DEFAULT_SUFFIX):  # noqa
    """
    Parse a dictionnary and grab all variable under a custom
    prefix inside the same prefixed dict:
    eg::

        {'a_1': 'aaa', 'a_2': 'bbb' } | copsf_to_namespace('a') =>
        {'a': {'1': 'aaa', '2': 'bbb'}}

    """
    if namespaced is None:
        namespaced = {}
    if isinstance(sub_namespaced, list):
        sub_namespaced = {}
        for i in sub_namespaced:
            sub_namespaced[i] = {}
    if sub_namespaced is None:
        sub_namespaced = namespaced.get(sub_registries_key, {})
    if flavors is None:
        flavors = []
    if prefixes is None:
        prefixes = set()
    if do_load_overrides is None:
        do_load_overrides = False
    name_prefix = get_name_prefix(name_prefix, prefix)
    prefixes.add(prefix)
    for ns in sub_namespaced:
        sub_prefix = prefix+ns+'_'
        prefixes.add(get_name_prefix(name_prefix, sub_prefix))
        prefixes.add(prefix)
    for var in six.iterkeys(ansible_vars):
        if (
            (var in prefixes) or
            (var.endswith(registry_suffix)) or
            (not var.startswith(prefix))
        ):
            continue
        svar = prefix.join(var.split(prefix)[1:])
        namespaced.update({svar: ansible_vars[var]})
    for ns, sub_sub_namespaced in six.iteritems(sub_namespaced):
        sub_prefix = prefix+ns+'_'
        namespaced[ns], ansible_vars = copsf_to_namespace(
            ansible_vars,
            sub_prefix,
            do_load_overrides=do_load_overrides,
            overrides_prefix=overrides_prefix,
            flavors=flavors,
            name_prefix=name_prefix,
            sub_namespaced=sub_sub_namespaced,
            namespaced=namespaced.setdefault(ns, {}),
            registry_suffix=registry_suffix)
        for sv, ssval in six.iteritems(namespaced[ns]):
            namespaced.update({ns+'_'+sv: ssval})
    if knobs:
        namespaced = copsf_knobs(ansible_vars,
                                 namespaced,
                                 knobs,
                                 flavors=flavors)
    if computed_defaults:
        namespaced = copsf_compute_defaults(ansible_vars,
                                            namespaced,
                                            computed_defaults)
    if lowered:
        namespaced = copsf_compute_lower(ansible_vars,
                                         namespaced,
                                         lowered)
    if subos_append:
        copsf_subos_append(ansible_vars,
                           namespaced,
                           sub_namespaced,
                           subos_append)
    namespaces = get_subnamespaces(namespaced,
                                   sub_namespaced=sub_namespaced,
                                   sub_registries_key=sub_registries_key)
    for v, val in six.iteritems(namespaced):
        if '_' not in v:
            continue
        nsparts = v.split('_')
        for i in range(len(nsparts)):
            part = '_'.join(nsparts[:i])
            key = '_'.join(nsparts[i:])
            if part in namespaces:
                sns = namespaces[part]
                if key in sns:
                    sns[key] = val
    if do_load_overrides:
        namespaced = copsf_load_registry_overrides(
            ansible_vars,
            prefix,
            overrides_prefix=overrides_prefix,
            registry=namespaced)

    return namespaced, ansible_vars


def get_subnamespaces(namespaced,
                      namespaces=None,
                      prefix=None,
                      sub_namespaced=None,
                      sub_registries_key=SUBREGISTRIES_KEYS):
    if namespaces is None:
        namespaces = {}
    if sub_namespaced is None:
        sub_namespaced = namespaced.get(sub_registries_key, {})
    for i, sns in six.iteritems(sub_namespaced):
        sub_prefix = prefix and (prefix+'_'+i) or i
        snamespace = namespaced.get(i, {})
        namespaces = get_subnamespaces(snamespace,
                                       namespaces=namespaces,
                                       prefix=sub_prefix,
                                       sub_registries_key=sub_registries_key)
        namespaces[sub_prefix] = snamespace
    return namespaces


def copsf_subos_append(ansible_vars,
                       namespaced,
                       sub_namespaced,
                       subos_append):
    for _os in subos_append:
        if ansible_vars['ansible_lsb']['id'].lower() == _os:
            for v in subos_append[_os]['vars']:
                vn = '{0}_{1}'.format(v, subos_append[_os]['os'])
                if v in namespaced and vn in namespaced:
                    namespaced[v].extend(namespaced[vn])
    return namespaced

def copsf_registry(ansible_vars,
                   prefix,
                   do_load_overrides=None,
                   do_format_resolve=None,
                   do_to_vars=True,
                   knobs=None,
                   subos_append=None,
                   computed_defaults=None,
                   lowered=None,
                   flavors=None,
                   overrides_prefix=None,
                   namespaced=None,
                   global_scope=None,
                   name_prefix=None,
                   sub_namespaced=None,
                   registry_suffix=REGISTRY_DEFAULT_SUFFIX,
                   **kw):
    name_prefix = get_name_prefix(name_prefix, prefix)
    ansible_vars = copsf_reset_vars_from_registry(
        ansible_vars, prefix,
        registry_suffix=registry_suffix)
    namespaced, ansible_vars = copsf_to_namespace(
        ansible_vars,
        prefix,
        do_load_overrides=do_load_overrides,
        knobs=knobs,
        subos_append=subos_append,
        computed_defaults=computed_defaults,
        lowered=lowered,
        flavors=flavors,
        overrides_prefix=overrides_prefix,
        namespaced=namespaced,
        name_prefix=name_prefix,
        sub_namespaced=sub_namespaced,
        registry_suffix=registry_suffix)
    if do_format_resolve:
        namespaced = copsf_format_resolve(namespaced)
    if do_to_vars:
        namespaced, ansible_vars = copsf_registry_to_vars(
            namespaced,
            ansible_vars,
            prefix,
            global_scope=global_scope,
            name_prefix=name_prefix,
            registry_suffix=registry_suffix)
    return namespaced, ansible_vars


def copsf_cwd(*args, **kw):
    return os.getcwd()


__funcs__ = {
    'copsf_cwd': copsf_cwd,
    'copsf_to_lower': copsf_to_lower,
    'copsf_format_val': copsf_format_val,
    'copsf_registry_to_vars': copsf_registry_to_vars,
    'copsf_registry': copsf_registry,
    'copsf_to_namespace': copsf_to_namespace,
    'copsf_knobs': copsf_knobs,
    'copsf_compute_defaults': copsf_compute_defaults,
    'copsf_compute_lower': copsf_compute_lower,
    'copsf_format_resolve': copsf_format_resolve,
    'copsf_splitstrip': splitstrip,
    'copsf_looseversion': looseversion,
    'copsf_dictupdate': dictupdate,
    'copsf_deepcopy': cops_deepcopy,
    'copsf_copy': cops_copy,
    'copsf_api_wait_lock': wait_lock,
    'copsf_wait_lock': wait_lock,
    'copsf_api_hash_value': hash_value,
    'copsf_hash_value': hash_value,
    'copsf_api_dirname': dirname,
    'copsf_dirname': dirname,
    'copsf_api_basename': basename,
    'copsf_basename': basename,
    'copsf_bool': copsf_bool,
    'copsf_asbool': copsf_bool,
    'copsf_pdb': go_pdb,
    'copsf_islist': lambda x: is_typ_(x, list),
    'copsf_isdict': lambda x: is_typ_(x, dict),
    'copsf_isset': lambda x: is_typ_(x, set),
    'copsf_istuple': lambda x: is_typ_(x, tuple),
    'copsf_isint': lambda x: is_typ_(x, int),
    'copsf_isbool': lambda x: is_typ_(x, bool),
    'copsf_isstr': lambda x: is_typ_(x, six.string_types),
    'copsf_isu': lambda x: is_typ_(x, unicode),
    'copsf_isfloat': lambda x: is_typ_(x, float),
    'copsf_islong': lambda x: is_typ_(x, long),
    'copsf_isnum': lambda x: is_typ_(x, long),
    'cops_basename': basename,  # retrocompat
    'copsf_api_secure_password': secure_password,
    'copsf_secure_password': secure_password,
    'copsf_api_rand_value': rand_value,
    'copsf_rand_value': rand_value,
}


class FilterModule(object):

    def filters(self):
        return __funcs__
# vim:set et sts=4 ts=4 tw=80
