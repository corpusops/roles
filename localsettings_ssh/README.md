# corpusops.roles/localsettings_ssh ansible role
## Documentation
**WARNING**: The role locks ssh for users that belongs to 'sshusers' group by default
## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/localsettings_ssh/role.yml \
   -t corpusops.roles/localsettings_ssh_vars
```
