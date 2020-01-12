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

import copy
import ipaddr
from ansible.module_utils import six
import contextlib
import socket
import re
from ansible.module_utils import six

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


def copsf_append_templates_dir_to_default_abs_template_path(val):
    if isinstance(val, six.string_types) and val.startswith('/'):
        val = 'templates{0}'.format(val)
    return val


__funcs__ = {
    'copsf_append_templates_dir_to_default_abs_template_path': copsf_append_templates_dir_to_default_abs_template_path,
}


class FilterModule(object):

    def filters(self):
        return __funcs__
# vim:set et sts=4 ts=4 tw=80
