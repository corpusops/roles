#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import os
import logging

__fn = os.path.abspath(__file__)
__n = os.path.splitext(os.path.basename(__fn))[0]
__mod = os.path.dirname(__fn)
__pmod = os.path.dirname(__mod)
log = logging.getLogger(__n)
__metaclass__ = type
with open(os.path.join(__mod, '../api/cops_load.python')) as fic:
    exec(fic.read(), globals(), locals())


def load(data):
    content = data.replace(' ---ANTLISLASH_N--- ', '\n')
    content = json.loads(content)
    return content


def dump(data, pretty=False):
    if pretty:
        content = json.dumps(data, indent=4, separators=(',', ': '))
    else:
        content = json.dumps(data)
        content = content.replace('\n', ' ---ANTLISLASH_N--- ')
    return content


__funcs__ = {
    'copsf_json_load': load,
    'copsf_json_dump': dump,
}


class FilterModule(object):

    def filters(self):
        return __funcs__
# vim:set et sts=4 ts=4 tw=80:
