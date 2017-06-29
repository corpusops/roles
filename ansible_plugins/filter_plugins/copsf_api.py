#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import six
import time
import os
import contextlib
import hashlib
import logging
import fcntl
import tempfile
import random
import string
import re

try:
    import Crypto.Random  # pylint: disable=E0611
    HAS_RANDOM = True
except ImportError:
    HAS_RANDOM = False


__fn = os.path.abspath(__file__)
__n = os.path.splitext(os.path.basename(__fn))[0]
__mod = os.path.dirname(__fn)
__pmod = os.path.dirname(__mod)
log = logging.getLogger(__n)
__metaclass__ = type
with open(os.path.join(__mod, '../api/cops_load.python')) as fic:
    exec(fic.read(), globals(), locals())


class LockError(Exception):
    '''.'''


def lock(fd, flags=fcntl.LOCK_NB | fcntl.LOCK_EX):
    fcntl.flock(fd.fileno(), flags)


def unlock(fd):
    fcntl.flock(fd.fileno(), fcntl.LOCK_UN)


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


def secure_password(length=None, use_random=True, *args, **kwargs):
    '''
    Generate a secure password.
    '''
    if not length:
        length = 16
    length = int(length)
    pw = ''
    while len(pw) < length:
        if HAS_RANDOM and use_random:
            pw += re.sub(r'\W', '', Crypto.Random.get_random_bytes(1))
        else:
            pw += random.SystemRandom().choice(
                string.ascii_letters + string.digits)
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
    return type(val) in typs_


def go_pdb(val=None, *args,  **kwargs):
    from pdb_clone import pdb as pdbc
    pdbc.set_trace_remote()


def cops_bool(value, asbool=True):
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


__funcs__ = {
    'copsf_api_wait_lock': wait_lock,
    'copsf_api_hash_value': hash_value,
    'copsf_api_dirname': dirname,
    'copsf_api_basename': basename,
    'cops_bool': cops_bool,
    'cops_pdb': go_pdb,
    'cops_islist': lambda x: is_typ_(x, list),
    'cops_isdict': lambda x: is_typ_(x, dict),
    'cops_isset': lambda x: is_typ_(x, set),
    'cops_istuple': lambda x: is_typ_(x, tuple),
    'cops_isint': lambda x: is_typ_(x, int),
    'cops_isbool': lambda x: is_typ_(x, bool),
    'cops_isstr': lambda x: is_typ_(x, six.string_types),
    'cops_isu': lambda x: is_typ_(x, unicode),
    'cops_isfloat': lambda x: is_typ_(x, float),
    'cops_islong': lambda x: is_typ_(x, long),
    'cops_isnum': lambda x: is_typ_(x, long),
    'cops_basename': basename,  # retrocompat
    'copsf_api_secure_password': secure_password,
    'copsf_api_rand_value': rand_value,
}


class FilterModule(object):

    def filters(self):
        return __funcs__
# vim:set et sts=4 ts=4 tw=80:
