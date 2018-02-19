from __future__ import (absolute_import, division, print_function)

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.module_utils._text import to_native
from ansible.plugins.action import ActionBase
import re


DBUS_RE = re.compile('failed.*d?-?bus', re.I|re.U|re.M)

__metaclass__ = type


class ActionModule(ActionBase):

    TRANSFERS_FILES = True

    UNUSED_PARAMS = {
        'systemd': ['pattern', 'runlevel', 'sleep', 'arguments', 'args'],
        'service': ['daemon_reload'],
        'upstart': ['daemon_reload'],
    }

    def run(self, tmp=None, task_vars=None, *args, **kw):
        '''.'''
        if task_vars is None:
            task_vars = dict()
        self._supports_check_mode = True
        self._supports_async = True

        result = super(ActionModule, self).run(tmp, task_vars)

        module = self._task.args.get('use', 'auto').lower()

        if module == 'auto':
            try:
                if self._task.delegate_to: # if we delegate, we should use delegated host's facts
                    module = self._templar.template("{{hostvars['%s']['ansible_service_mgr']}}" % self._task.delegate_to)
                else:
                    module = self._templar.template('{{ansible_service_mgr}}')
            except Exception:
                pass  # could not get it from template!

        if module == 'auto':
            facts = self._execute_module(module_name='setup', module_args=dict(gather_subset='!all', filter='ansible_service_mgr'), task_vars=task_vars)
            self._display.debug("Facts %s" % facts)
            if 'ansible_facts' in facts and  'ansible_service_mgr' in facts['ansible_facts']:
                module = facts['ansible_facts']['ansible_service_mgr']

        if not module or module == 'auto' or module not in self._shared_loader_obj.module_loader:
            module = 'service'

        if module != 'auto':
            new_module_args = self._task.args.copy()
            if module == 'systemd':
                margs = (self._task,
                         self._connection,
                         self._play_context,
                         self._loader,
                         self._templar,
                         self._shared_loader_obj)
                self._ah = self._shared_loader_obj.action_loader.get(
                    'cops_actionhelper', *margs)
                ret = self._ah.exec_command(
                    'systemctl --no-pager is-system-running')
                # if connection to dbus is possible, systemd is running somehow
                if DBUS_RE.search(ret['stderr']):
                    module = 'cops_systemd'
            # run the 'service' module
            if 'use' in new_module_args:
                del new_module_args['use']

            # for backwards compatibility
            if 'state' in new_module_args and new_module_args['state'] == 'running':
                new_module_args['state'] = 'started'

            if module in self.UNUSED_PARAMS:
                for unused in self.UNUSED_PARAMS[module]:
                    if unused in new_module_args:
                        del new_module_args[unused]
                        self._display.warning('Ignoring "%s" as it is not used in "%s"' % (unused, module))

            self._display.vvvv("Running %s" % module)
            result.update(self._execute_module(module_name=module, module_args=new_module_args, task_vars=task_vars))
        else:
            result['failed'] = True
            result['msg'] = 'Could not detect which service manager to use. Try gathering facts or setting the "use" option.'
        return result
