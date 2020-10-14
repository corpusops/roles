# corpusops.roles/localsettings_hostname ansible role
## Documentation

- Set machine hostname
- vars:
    - ``corpusops_localsettings_hostname_hostname``: hostname
    - ``corpusops_localsettings_hostname_fqdn``: fqdn

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/localsettings_hostname/role.yml \
   -t corpusops.roles/localsettings_hostname_vars
```
