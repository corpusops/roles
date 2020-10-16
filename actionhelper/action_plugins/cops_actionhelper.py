from __future__ import (absolute_import, division, print_function)

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.module_utils._text import to_native
from ansible.plugins.action import ActionBase

__metaclass__ = type


class ActionHelperError(Exception):
    '''.'''


class CommandNotFound(ActionHelperError):
    '''.'''

_GET_COMMAND = '''
get_command() {
    local p=
    local cmd="${@}"
    if which which >/dev/null 2>/dev/null;then
        p=$(which "${cmd}" 2>/dev/null)
    fi
    if [ "x${p}" = "x" ];then
        p=$(export IFS=:;
            echo "${PATH-}" | while read -ra pathea;do
                for pathe in "${pathea[@]}";do
                    pc="${pathe}/${cmd}";
                    if [ -x "${pc}" ]; then
                        p="${pc}"
                    fi
                done
                if [ "x${p}" != "x" ]; then echo "${p}";break;fi
            done )
    fi
    if [ "x${p}" != "x" ];then
        echo "${p}"
    fi
}
'''

class ActionModule(ActionBase):

    TRANSFERS_FILES = True
    _forwarded_task_vars = None

    def set_forwarded_task_vars(self, v):
        self._forwarded_task_vars = v
        return v

    def run(self, *args, **kw):
        '''.'''

    def exec_module(self, module_name, *args, **kwargs):
        if kwargs is None:
            kwargs = {}
        kwargs.setdefault('delete_remote_tmp',
                          kwargs.get('tmp', None))
        if self._forwarded_task_vars:
            kwargs.setdefault('task_vars', self._forwarded_task_vars)
        ret = self._execute_module(module_name, *args, **kwargs)

        return ret

    def exec_command(self, cmd):
        return self.exec_module('command', {'_uses_shell': True,
                                            '_raw_params': cmd})

    def which(self, cmd):
        _cmd = _GET_COMMAND + 'get_command {0}'.format(cmd)
        cmd_ = ''
        ret = self.exec_command(_cmd)
        if ret['rc'] == 0 and ret['stdout']:
            cmd_ = ret['stdout'].strip()
        else:
            raise CommandNotFound(cmd)
        return cmd_
