#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.service import sysv_exists, sysv_is_enabled, fail_if_missing
from ansible.module_utils._text import to_native

DOCUMENTATION = '''
module: cops_service
author:
    - "Ansible Core Team"
version_added: "2.2"
short_description:  Manage services.
description:
options:
'''

EXAMPLES = '''
'''

RETURN = '''
'''


def main():
    # initialize
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True, type='str',
                      aliases=['unit', 'service']),
            state=dict(choices=['started', 'stopped', 'restarted', 'reloaded'],
                       type='str'),
            enabled=dict(type='bool'),
            masked=dict(type='bool'),
            daemon_reload=dict(type='bool', default=False,
                               aliases=['daemon-reload']),
            user=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
        required_one_of=[['state', 'enabled', 'masked', 'daemon_reload']],
    )
    systemctl = module.get_bin_path('systemctl')
    from pdb_clone import pdb as pdbc;pdbc.set_trace_remote()  ## Breakpoint ##
    tgtp = '/etc/systemd/system/multi-user.target.wants'
    paths = ['/etc/systemd/system',
             '/run/systemd/system',
             '/lib/systemd/system']
    if module.params['user']:
        systemctl = systemctl + " --user"
        paths = ['$XDG_CONFIG_HOME/systemd/user',
                 '$HOME/.config/systemd/user',
                 '/etc/systemd/user',
                 '$XDG_RUNTIME_DIR/systemd/user',
                 '/run/systemd/user',
                 '$XDG_DATA_HOME/systemd/user',
                 '$HOME/.local/share/systemd/user',
                 '/usr/lib/systemd/user']
    unit = module.params['name']
    rc = 0
    out = err = ''
    changed = False
    result = {
        'name':  unit,
        'changed': False,
        'status': {},
        'warnings': [],
    }
    done = []
    suffixed = re.compile(
        '\.(service|socket|unit|mount)', re.M | re.I | re.U)
    if module.params['enabled'] in (True, False):
        funit = unit
        if not suffixed.search(funit):
            funit += '.service'
        cmd = 'find {0} -name {1} |grep -v wants| head -n1'.format(
                ' '.join(paths), funit)
        (rc, out, err) = module.run_command(cmd, use_unsafe_shell=True)
        out = (out or '').strip()
        if not (out and os.path.exists(out)):
            module.fail_json(rc=256,
                             msg="unit not found: {0}".format(funit))
        else:
            bout = os.path.basename(out)
            tgt = os.path.join(tgtp, bout)
            if not os.path.exists(tgtp):
                os.makedirs(tgtp)
                done.append('Created target: {0}'.format(tgtp))
                changed = True
            if os.path.exists(tgt) or os.path.islink(tgt):
                rp = os.readlink(tgt)
                if (rp != out) or not module.params['enabled']:
                    os.unlink(tgt)
                    done.append('Removed stale link: {0}'.format(tgt))
                    changed = True
            if module.params['enabled'] and not os.path.exists(tgt):
                os.symlink(out, tgt)
                done.append('Created: {0} -> {1}'.format(tgt, out))
                changed = True
            result['cops_service'] = done
            result['changed'] = changed
    module.exit_json(**result)


if __name__ == '__main__':
    main()
