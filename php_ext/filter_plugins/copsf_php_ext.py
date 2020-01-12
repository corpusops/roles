#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from ansible.module_utils import six
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


def splitstrip(a, splitter=None):
    ret = []
    if isinstance(a, six.string_types):
        a = a.split()
    if isinstance(a, list):
        for i in a:
            if isinstance(i, six.string_types):
                i = i.strip()
            ret.append(i)
    return ret


def cops_sapi(sapi, all_sapi=None):
    ret = set()
    all_sapi = splitstrip(all_sapi)
    if not isinstance(sapi, list):
        sapi = sapi.split()
    for i in sapi:
        if i.lower() == 'all':
            [ret.add(a) for a in all_sapi]
        else:
            ret.add(i)
    return [a for a in ret]


__funcs__ = {
    'cops_sapi': cops_sapi,
}


class FilterModule(object):

    def filters(self):
        return __funcs__
# vim:set et sts=4 ts=4 tw=80:
# vim:set et sts=4 ts=4 tw=80:
