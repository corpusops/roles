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


def copsf_where(*args, **kw):
    with open('/etc/hostname') as f:
        return f.read()


__funcs__ = {
    'copsf_where': copsf_where,
}


class FilterModule(object):

    def filters(self):
        return __funcs__
# vim:set et sts=4 ts=4 tw=80:
# vim:set et sts=4 ts=4 tw=80:
