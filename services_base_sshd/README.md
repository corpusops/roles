# corpusops.roles/services_base_sshd ansible role
## Documentation
**WARNING**: The role locks sshd for users that belongs to 'sshusers' group by default
## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/services_base_sshd/role.yml \
   -t corpusops.roles/services_base_sshd_vars
```
