# corpusops.roles/localsettings_packer ansible role
## Documentation
Needs to be applied before (next line should be on one line (parsed during tests)):
- cops roles dependencies: corpusops.roles/localsettings_profile

- This installs packer in `/opt` and links into your PATH (`/usr/local`)
- All the behavior can be tweaked by variables (`corpusops_localsettings_packer_`)

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/localsettings_packer_vars/role.yml
```

## installing hashicorp-packer from direct url(binaries)
```yaml
- hosts: all
  roles: [corpusops.roles/localsettings_packer]
  vars:
    corpusops_localsettings_packer_version: "1.0.0"
```
