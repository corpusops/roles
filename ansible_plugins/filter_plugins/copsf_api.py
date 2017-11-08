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


def copsf_compute_vars(ansible_vars, prefix,
                       lowered=None, computed_defaults=None):
    vals = []
    if computed_defaults is None:
        computed_defaults = []
    if lowered is None:
        lowered = []
    for k in computed_defaults:
        svar = prefix + k
        if svar not in ansible_vars:
            continue
        val = copsf_format_val(ansible_vars[svar], ansible_vars)
        vals.append(val)
        ansible_vars.update({svar: val})
    for k in lowered:
        svar = prefix + k
        if svar not in ansible_vars:
            continue
        val = copsf_to_lower(ansible_vars[svar])
        ansible_vars.update({svar: val})
    return ansible_vars


def copsf_registry_to_vars(namespaced, ansible_vars, prefix):
    for k, val in six.iteritems(namespaced):
        ansible_vars.update({prefix+k: val})
    return namespaced, ansible_vars


def copsf_knobs(ansible_vars, prefix,
                subos_append=None, knobs=None, flavors=None):
    """
    Per os knobs to filter variables and prepare registry adapting to
    the environment target OS
    """
    if knobs is None:
        knobs = []
    if flavors is None:
        flavors = []
    if subos_append is None:
        subos_append = {}
    for v in knobs:
        vn = prefix + v
        if ansible_vars.get(vn, None) is not None:
            continue
        for flav in flavors:
            if (
                flav == 'default' or
                ansible_vars['ansible_os_family'].lower() == flav or
                ansible_vars['ansible_lsb']['id'].lower() == flav
            ):
                os_vpref = vn + '_' + flav
                if os_vpref in ansible_vars:
                    ansible_vars.update({vn: ansible_vars[os_vpref]})
                    break
    for _os in subos_append:
        if ansible_vars['ansible_lsb']['id'].lower() == _os:
            for v in subos_append[_os]['vars']:
                sv = prefix+v
                vn = prefix+'{0}_{1}'.format(v, subos_append[_os]['os'])
                if sv in ansible_vars and vn in ansible_vars:
                    ansible_vars[prefix+v].extend(ansible_vars[vn])
    return ansible_vars


def copsf_to_namespace(ansible_vars,
                       prefix,
                       computed_defaults=None,
                       lowered=None,
                       sub_namespaced=None,
                       flavors=None,
                       namespaced=None):
    """
    Parse a dictionnary and grab all variable under a custom
    prefix inside the same prefixed dict:
    eg::

        {'a_1': 'aaa', 'a_2': 'bbb' } | copsf_to_namespace('a') =>
        {'a': {'1': 'aaa', '2': 'bbb'}}

    """
    if namespaced is None:
        namespaced = {}
    if sub_namespaced is None:
        sub_namespaced = {}
    if flavors is None:
        flavors = []
    vprefix = prefix+'vars'
    for var in six.iterkeys(ansible_vars):
        if var == vprefix or not var.startswith(prefix):
            continue
        svar = prefix.join(var.split(prefix)[1:])
        for flav in flavors:
            if (
                var.endswith('_'+flav) and
                var.split('_'+flav)[0] in ansible_vars
            ):
                continue
        for ns in sub_namespaced:
            if not var.startswith(prefix+ns+'_'):
                continue
            svar = var.replace(prefix+ns+'_', '')
            sub_namespaced.setdefault(
                ns, {}).update({svar: ansible_vars[var]})
            namespaced.update({ns: sub_namespaced[ns]})
        namespaced.update({svar: ansible_vars[var]})

    namespaced, ansible_vars = copsf_registry_to_vars(
        namespaced, ansible_vars, prefix)
    return namespaced, ansible_vars


def copsf_registry(ansible_vars,
                   prefix,
                   do_os_knobs=True,
                   do_resolve=True,
                   knobs=None,
                   subos_append=None,
                   computed_defaults=None,
                   lowered=None,
                   flavors=None,
                   namespaced=None,
                   sub_namespaced=None):
    if do_os_knobs:
        ansible_vars = copsf_knobs(ansible_vars,
                                   prefix,
                                   subos_append=subos_append,
                                   knobs=knobs,
                                   flavors=flavors)
    if do_resolve:
        ansible_vars = copsf_compute_vars(
            ansible_vars, prefix,
            lowered=lowered,
            computed_defaults=computed_defaults)
    namespaced, ansible_vars = copsf_to_namespace(
        ansible_vars,
        prefix,
        sub_namespaced=sub_namespaced,
        flavors=flavors,
        namespaced=namespaced)
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
    'copsf_compute_vars': copsf_compute_vars,
    'copsf_format_resolve': format_resolve,
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
