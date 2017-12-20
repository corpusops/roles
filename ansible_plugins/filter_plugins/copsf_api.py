#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import six
import time
import collections
import cProfile
import os
import contextlib
import hashlib
import logging
import fcntl
import copy
import traceback
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


_STR_RESOLVED_CACHE = {}
_RESOLVED_CACHE = {}
is_really_a_var = re.compile('(\{[^}]+\})', re.M | re.U)
__fn = os.path.abspath(__file__)
__n = os.path.splitext(os.path.basename(__fn))[0]
__mod = os.path.dirname(__fn)
__pmod = os.path.dirname(__mod)
log = logging.getLogger(__n)
__metaclass__ = type
_DEFAULT = object()
REGISTRY_PREFIX_KEY = '__cops_registry_prefix__ '
SUBREGISTRIES_KEYS = 'cops_sub_namespaces'
REGISTRYVARS_SUFFIX = 'vars'
REGISTRY_DEFAULT_SUFFIX = '_REGISTRY_DEFAULT'
REGISTRY_DEFAULT_VALUE = '_CORPUSOPS_DEFAULT_VALUE'
single_brance_in_re = re.compile('(^|[^{])({)[^{]', flags=re.M | re.U)
single_brance_out_re = re.compile('[^}](})([^}]|$)', flags=re.M | re.U)
double_brance_in_re = re.compile('{{', flags=re.M | re.U)
double_brance_out_re = re.compile('}}', flags=re.M | re.U)

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


def abspath(sstring):
    return os.path.abspath(sstring)


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
    else:
        return True


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


def unresolved(data, jinja=None):
    iddata = id(data)
    if jinja is None:
        jinja = True
    try:
        jcache = _RESOLVED_CACHE[jinja]
    except KeyError:
        jcache = _RESOLVED_CACHE[jinja] = {}
    try:
        ret = jcache[iddata]
    except KeyError:
        ret = None
    if ret is not None:
        return ret
    if isinstance(data, six.string_types):
        if '{' in data and '}' in data:
            if is_really_a_var.search(data):
                ret = True
            else:
                ret = False
            if ret and jinja and ('{{' in data) and ('}}' in data):
                jbraces_in = len(single_brance_in_re.findall(data))
                jbraces_out = len(single_brance_out_re.findall(data))
                ret = ((jbraces_in+jbraces_out) % 2 != 0)
                # if we detected jinja markers {{foo}}
                if not ret:
                    # we also check that we do not have still regular
                    # python {foo} strings left
                    single_braces_in = len(single_brance_in_re.findall(data))
                    single_braces_out = len(single_brance_out_re.findall(data))
                    if single_braces_in and single_braces_out:
                        ret = single_braces_in == single_braces_out
        else:
            ret = False
    elif isinstance(data, dict):
        for k, val in six.iteritems(data):
            # if unresolved(k, jinja=jinja):
            #    break
            if unresolved(val, jinja=jinja):
                return True
    elif isinstance(data, (list, set)):
        for val in data:
            if unresolved(val, jinja=jinja):
                return True
    _RESOLVED_CACHE[jinja][iddata] = ret
    return ret


def _str_resolve(new,
                 original_dict=None,
                 jinja=None,
                 this_call=0,
                 topdb=False):

    '''
    low level and optimized call to format_resolve
    '''
    if jinja is None:
        jinja = True
    init_new = new
    # do not directly call format to handle keyerror in original mapping
    # where we may have yet keyerrors
    unresolved_state = unresolved(new, jinja=jinja)
    if unresolved_state and isinstance(original_dict, dict):
        for k in original_dict:
            reprk = k
            if not isinstance(reprk, six.string_types):
                reprk = '{0}'.format(k)
            jsubst = '{{'+reprk+'}}'
            subst = '{'+reprk+'}'
            if jsubst in new:
                continue
            elif subst in new:
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
            unresolved_state = unresolved(new, jinja=jinja)
            if not unresolved_state:
                # new value has been totally resolved
                break
    # if still unresolved try to fallback on python's resolve
    if unresolved_state:
        try:
            fnew = new
            if jinja:
                # escape jinja strings
                try:
                    fnew.index('{{')
                    fnew.index('}}')
                    fnew = fnew.replace('{{', '{{{{').replace('}}', '}}}}')
                except Exception:
                    pass
                try:
                    fnew.index('{%')
                    fnew.index('%}')
                    fnew = fnew.replace('{%', '{{%').replace('%}', '%}}')
                except Exception:
                    pass
            new = fnew.format(**original_dict)
            unresolved_state = unresolved(new, jinja=jinja)
        except Exception:
            pass
    return new, new != init_new, unresolved_state


def str_resolve(new, original_dict=None, this_call=0, topdb=False, jinja=None):
    return _str_resolve(
        new,
        original_dict=original_dict,
        this_call=this_call,
        topdb=topdb,
        jinja=jinja)[0]


def _format_resolve(value,
                    original_dict=None,
                    this_call=0,
                    topdb=False,
                    retry=None,
                    jinja=True,
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

    unresolved_state = unresolved(value, jinja=jinja)
    if not unresolved_state:
        return value, False, False

    if isinstance(value, six.string_types):
        new, changed_, unresolved_state_ = _str_resolve(
            value, original_dict, jinja=jinja, topdb=topdb)
        unresolved_state = unresolved_state or unresolved_state_
        changed = changed_ or changed
    elif isinstance(value, dict):
        new = type(value)()
        for key, v in value.items():
            val, changed_, unresolved_state_ = _format_resolve(
                v, original_dict, jinja=jinja, topdb=topdb)
            unresolved_state = unresolved_state or unresolved_state_
            changed = changed_ or changed
            new[key] = val
    elif isinstance(value, (list, tuple)):
        new = type(value)()
        for v in value:
            val, changed_, unresolved_state_ = _format_resolve(
                v, original_dict, jinja=jinja, topdb=topdb)
            unresolved_state = unresolved_state or unresolved_state_
            changed = changed_ or changed
            new = new + type(value)([val])
    else:
        new = value

    if unresolved_state:
        if retry is None:
            retry = True
    else:
        retry = False

    while retry and (this_call < 100):
        new, changed, unresolved_state = _format_resolve(
            new,
            original_dict,
            jinja=jinja,
            this_call=this_call,
            retry=False,
            topdb=topdb)
        if not changed:
            retry = False
        this_call += 1
    return new, changed, unresolved_state


def format_resolve(value,
                   original_dict=None,
                   jinja=None,
                   this_call=0,
                   topdb=False,
                   additional_namespaces=None,
                   **kwargs):
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
    topdb2 = kwargs.pop('topdb2', False)  # noqa
    if additional_namespaces is None:
        additional_namespaces = {}
    if isinstance(additional_namespaces, dict):
        additional_namespaces = [additional_namespaces]
    if isinstance(original_dict, list):
        if original_dict:
            for i in original_dict[1:]:
                additional_namespaces.insert(0, i)
            original_dict = original_dict[0]
    try:
        ret = _format_resolve(value,
                              original_dict=original_dict,
                              jinja=jinja,
                              this_call=this_call,
                              topdb=topdb,
                              **kwargs)
        for namespace in additional_namespaces:
            if ret[2]:
                ret = _format_resolve(ret[0],
                                      original_dict=namespace,
                                      jinja=jinja,
                                      this_call=this_call,
                                      topdb=topdb,
                                      **kwargs)
                if not ret[2]:
                    break
    except Exception as exc:
        trace = traceback.format_exc()
        raise exc
    return ret[0]


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


def get_name_prefix(name_prefix,
                    prefix,
                    suffix=REGISTRYVARS_SUFFIX):
    if not name_prefix:
        name_prefix = prefix + suffix
    return name_prefix


def copsf_reset_vars_from_registry(ansible_vars,
                                   prefix,
                                   name_prefix,
                                   registryvars_suffix=REGISTRYVARS_SUFFIX,
                                   registry_suffix=REGISTRY_DEFAULT_SUFFIX):  #noqa
    dsvars = ansible_vars.setdefault('__'+prefix+registry_suffix, {})
    name_prefix = get_name_prefix(name_prefix,
                                  prefix,
                                  registryvars_suffix)
    old_vars = ansible_vars.pop(name_prefix, {})
    sprefixes = (prefix, prefix+prefix)
    prefixes = [name_prefix, prefix[:-1]]
    for var in [
        a for a in ansible_vars
        if (
            a.startswith(sprefixes) and
            a not in prefixes
        )
    ]:
        svar = var.split(prefix, 1)[1]
        reg_val = dsvars.get(svar, REGISTRY_DEFAULT_VALUE)
        cur_val = ansible_vars.get(var, REGISTRY_DEFAULT_VALUE)
        old_val = old_vars.get(svar, REGISTRY_DEFAULT_VALUE)
        if (
            cur_val == REGISTRY_DEFAULT_VALUE or
            reg_val == REGISTRY_DEFAULT_VALUE
        ):
            continue
        if (reg_val == old_val and reg_val != cur_val):
            dsvars[var] = cur_val
            continue
        ansible_vars[var] = reg_val
    return ansible_vars


def register_default_val(ansible_vars, variable, prefix,
                         registry_suffix, sub_registries_key,
                         method='setdefault'):
    sdvars = '__'+prefix+registry_suffix
    default_vars = ansible_vars.setdefault(sdvars, {})
    svar = prefix + variable
    value = ansible_vars.get(svar, REGISTRY_DEFAULT_VALUE)
    if (
        value != REGISTRY_DEFAULT_VALUE and
        variable not in [
            sub_registries_key
        ]
    ):
        getattr(default_vars, method)(variable, value)
    return ansible_vars


def copsf_registry_to_vars(namespaced,
                           ansible_vars,
                           prefix,
                           global_scope=None,
                           name_prefix=None,
                           do_format_resolve=False,
                           additional_namespaces=None,
                           registryvars_suffix=REGISTRYVARS_SUFFIX,
                           sub_registries_key=SUBREGISTRIES_KEYS,
                           registry_suffix=REGISTRY_DEFAULT_SUFFIX):
    name_prefix = get_name_prefix(name_prefix, prefix)
    scope = {}
    scope.update({name_prefix: namespaced})
    for k in [
        a for a in namespaced
        if not a.endswith((
            sub_registries_key))
    ]:
        svar = prefix + k
        scope[svar] = namespaced[k]
    sdvars = '__'+prefix+registry_suffix
    default_vars = ansible_vars.setdefault(sdvars, {})
    scope[sdvars] = default_vars
    ansible_vars.update(scope)
    if not global_scope:
        scope = namespaced
    if do_format_resolve:
        if additional_namespaces is None:
            additional_namespaces = [ansible_vars]
        scope = format_resolve(
            scope, additional_namespaces=additional_namespaces)
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


def copsf_load_registry_pre(ansible_vars,
                            prefix,
                            registry=None,
                            pre_prefix=None):
    if pre_prefix is None and prefix:
        pre_prefix = '{0}'.format(prefix[:-1])
    pre = ansible_vars.get(pre_prefix, {})
    registry = registry or ansible_vars.get(prefix, {})
    if (
        isinstance(pre, dict) and
        isinstance(registry, dict)
    ):
        for i, v in six.iteritems(pre):
            registry.setdefault(i, v)
    return registry


def copsf_load_registry_overrides(ansible_vars,
                                  prefix,
                                  registry=None,
                                  registry_suffix=REGISTRY_DEFAULT_SUFFIX,
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


def fill_sub_namespaces(origin,
                        element=None,
                        sub_namespaced=None,
                        sub_registries_key=SUBREGISTRIES_KEYS,
                        cprefix='',
                        oprefix='',
                        level=0,
                        ansible_vars=None,
                        parent=None):
    if not oprefix:
        oprefix = origin[REGISTRY_PREFIX_KEY]

    if element is None:
        element = origin.get(
            sub_registries_key, {}
        ).get(cprefix[:-1], {'value': None})['value']
        if element is None and ansible_vars:
            element = ansible_vars.get(
                oprefix+sub_registries_key, {})

    if isinstance(element, list):
        nsub_namespaced = {}
        for i in element:
            nsub_namespaced[i] = {}
        element = nsub_namespaced

    todo = {}
    if isinstance(element, dict):
        for i in [a for a in element]:
            val = element[i]
            if not val.get('cops_is_complex', False):
                todo[i] = element.pop(i)

    if sub_namespaced is None:
        sub_namespaced = element

    origin[sub_registries_key] = sub_namespaced
    if ansible_vars:
        ansible_vars[oprefix+sub_registries_key] = sub_namespaced

    for item, ssub_namespaced in six.iteritems(todo):
        k = cprefix+item
        val = sub_namespaced.setdefault(k, {})
        val['l'] = level
        val['cops_is_complex'] = True
        val['p'] = oprefix+cprefix + item + '_'
        val['k'] = k
        val.setdefault('children', [])
        val.setdefault('parents', [])
        if parent:
            parent['children'].append(k)
            val['parents'].extend(
                parent.get('parents', [])[:] + [parent['k']])
        if ssub_namespaced:
            fill_sub_namespaces(origin,
                                element=ssub_namespaced,
                                sub_namespaced=sub_namespaced,
                                cprefix=cprefix+item+'_',
                                oprefix=oprefix,
                                level=level+1,
                                parent=val,
                                ansible_vars=ansible_vars)
    if not level:
        sub_namespaced = copy.deepcopy(sub_namespaced)
    return sub_namespaced


def copsf_to_namespace(ansible_vars,
                       prefix,
                       do_load_registry_pre=None,
                       do_load_overrides=None,
                       do_format_resolve=None,
                       do_update_namespaces=None,
                       do_to_vars=None,
                       global_scope=None,
                       pre_prefix=None,
                       overrides_prefix=None,
                       sub_namespaced=None,
                       flavors=None,
                       name_prefix=None,
                       namespaced=None,
                       knobs=None,
                       lowered=None,
                       level=0,
                       computed_defaults=None,
                       format_resolve_topdb=None,
                       subos_append=None,
                       prefixes=None,
                       origin=None,
                       sub_registries_key=SUBREGISTRIES_KEYS,
                       registryvars_suffix=REGISTRYVARS_SUFFIX,  # noqa
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
    if prefixes is None:
        prefixes = []
    if do_load_registry_pre is None:
        do_load_registry_pre = True
    if do_load_registry_pre:
        namespaced = copsf_load_registry_pre(
            ansible_vars,
            prefix,
            pre_prefix=pre_prefix,
            registry=namespaced)
    name_prefix = get_name_prefix(None,
                                  prefix,
                                  suffix=registryvars_suffix)
    prefixes.append(prefix[:-1])
    prefixes.append(prefix)
    prefixes.append(name_prefix)
    origin_ = origin
    if origin is None:
        origin_ = namespaced
        namespaced[REGISTRY_PREFIX_KEY] = prefix
        sub_namespaced = fill_sub_namespaces(
            origin_,
            element=sub_namespaced,
            ansible_vars=ansible_vars,
            sub_registries_key=sub_registries_key)
    if sub_namespaced:
        snkeys = [a
                  for a in sorted([(sub_namespaced[a]['l'], a)
                                   for a in sub_namespaced])]
        rsnkeys = [a for a in reversed(snkeys)]
        for k in snkeys:
            d = sub_namespaced[k[1]]
            prefixes.append(get_name_prefix(None, d['p']))
    else:
        snkeys = rsnkeys = []
    ansible_vars_keys = [var for var in ansible_vars
                         if not (
                             (var in prefixes) or
                             (var.endswith(
                                 (registry_suffix))) or
                             (var.startswith(prefix+prefix)) or
                             (not var.startswith(prefix)))]
    for var in ansible_vars_keys:
        svar = var.split(prefix, 1)[1]
        ansible_vars = register_default_val(
            ansible_vars, svar, prefix,
            registry_suffix, sub_registries_key)
        namespaced[svar] = ansible_vars[var]
    # compute those args only after registry can give behavior !
    if subos_append is None:
        subos_append = namespaced.get('cops_subos_append', {})
    if lowered is None:
        lowered = namespaced.get('cops_lowered', [])
    if computed_defaults is None:
        computed_defaults = namespaced.get('cops_computed_defaults', [])
    if knobs is None:
        knobs = namespaced.get('cops_knobs', [])
    if global_scope is None:
        global_scope = namespaced.get('cops_global_scope', False)
    if do_update_namespaces is None:
        do_update_namespaces = namespaced.get('cops_do_update_namespaces', True)  # noqa
    if do_load_overrides is None:
        do_load_overrides = namespaced.get('cops_do_load_overrides', True)
    if do_to_vars is None:
        do_to_vars = namespaced.get('cops_do_to_vars', True)
    if format_resolve_topdb is None:
        format_resolve_topdb = namespaced.get('cops_format_resolve_topdb', False)  # noqa
    if do_format_resolve is None:
        do_format_resolve = namespaced.get('cops_do_format_resolve', False)
    if flavors is None:
        flavors = namespaced.get('cops_flavors', [])
    #
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

    if do_load_overrides:
        namespaced = copsf_load_registry_overrides(
            ansible_vars,
            prefix,
            overrides_prefix=overrides_prefix,
            registry_suffix=registry_suffix,
            registry=namespaced)

    if sub_namespaced and do_update_namespaces:
        for sns in rsnkeys:
            ns = sns[1]
            ns_data = sub_namespaced[ns]
            sub_k = ns_data['k']
            sub_p = sub_k + '_'
            sub_ns = namespaced.setdefault(sub_k, {})
            if not isinstance(sub_ns, dict):
                continue
            for i in [
                a for a in namespaced if a.startswith(sub_p)
            ]:
                kk = i.split(sub_p, 1)[1]
                kkval = namespaced[i]
                sub_ns[kk] = kkval

    if do_format_resolve and not level:
        namespaced = copsf_format_resolve(namespaced,
                                          additional_namespaces=[ansible_vars],
                                          topdb=format_resolve_topdb)
    if lowered:
        namespaced = copsf_compute_lower(ansible_vars,
                                         namespaced,
                                         lowered)
    scope = namespaced
    if level < 1 and do_to_vars:
        scope, ansible_vars = copsf_registry_to_vars(
            namespaced,
            ansible_vars,
            prefix,
            global_scope=global_scope,
            name_prefix=name_prefix,
            registryvars_suffix=registryvars_suffix,
            sub_registries_key=sub_registries_key,
            registry_suffix=registry_suffix)
    return scope, ansible_vars


def copsf_registry(ansible_vars,
                   prefix,
                   do_load_registry_pre=None,
                   do_load_overrides=None,
                   do_update_namespaces=None,
                   do_format_resolve=None,
                   do_to_vars=None,
                   knobs=None,
                   subos_append=None,
                   computed_defaults=None,
                   lowered=None,
                   flavors=None,
                   pre_prefix=None,
                   overrides_prefix=None,
                   namespaced=None,
                   global_scope=True,
                   name_prefix=None,
                   sub_namespaced=None,
                   profile=False,
                   registryvars_suffix=REGISTRYVARS_SUFFIX,
                   registry_suffix=REGISTRY_DEFAULT_SUFFIX,
                   update_mode=None,
                   **kw):
    pr = None
    if namespaced is not None and update_mode is None:
        update_mode = True
    if profile:
        pr = cProfile.Profile()
        pr.enable()
    name_prefix = get_name_prefix(name_prefix,
                                  prefix,
                                  registryvars_suffix)
    if not update_mode:
        ansible_vars = copsf_reset_vars_from_registry(
            ansible_vars, prefix, name_prefix,
            registryvars_suffix=registryvars_suffix,
            registry_suffix=registry_suffix)
    try:
        namespaced, ansible_vars = copsf_to_namespace(
            ansible_vars,
            prefix,
            do_load_registry_pre=do_load_registry_pre,
            do_load_overrides=do_load_overrides,
            do_format_resolve=do_format_resolve,
            do_to_vars=do_to_vars,
            do_update_namespaces=do_update_namespaces,
            knobs=knobs,
            subos_append=subos_append,
            computed_defaults=computed_defaults,
            lowered=lowered,
            flavors=flavors,
            global_scope=global_scope,
            pre_prefix=pre_prefix,
            overrides_prefix=overrides_prefix,
            namespaced=namespaced,
            name_prefix=name_prefix,
            registryvars_suffix=registryvars_suffix,
            sub_namespaced=sub_namespaced,
            registry_suffix=registry_suffix)
    except Exception:
        trace = traceback.format_exc()
        print(trace)
        raise
    if profile:
        pr.disable()
        fich, fic = tempfile.mkstemp()
        pr.dump_stats(fic + '_' + prefix + '_astat')
    return namespaced, ansible_vars


def copsf_scoped_registry(*args,  **kw):
    kw['global_scope'] = False
    return copsf_registry(*args, **kw)


def copsf_cwd(*args, **kw):
    return os.getcwd()


def uniquify(seq):
    '''uniquify a list'''
    seen = set()
    return [x for x in seq
            if x not in seen and not seen.add(x)]


__funcs__ = {
    'copsf_uniquify': uniquify,
    'copsf_cwd': copsf_cwd,
    'copsf_to_lower': copsf_to_lower,
    'copsf_format_val': copsf_format_val,
    'copsf_registry_to_vars': copsf_registry_to_vars,
    'copsf_registry': copsf_registry,
    'copsf_scoped_registry': copsf_scoped_registry,
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
    'copsf_abspath': abspath,
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
