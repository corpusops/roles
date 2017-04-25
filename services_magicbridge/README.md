# corpusops.services_magicbridge ansible role
## Documentation

Installs a script that create a hostonly bridge to connect to with dnsmasq & network masqueraging activated out of the box.

See [script](./templates/usr/bin/cops_magicbridge.sh)

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.services_magicbridge/role.yml \
   -t corpusops.services_magicbridge_vars
```
