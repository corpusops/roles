# corpusops.roles/services_virt_lxc ansible role
## Documentation

- Installs lxc on your host
- This will also install a linux network bridge called ``copslxcbr`` on the network <b>10.8/16</b>.

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/services_virt_lxc/role.yml \
   -t corpusops.roles/services_virt_lxc_vars
```
