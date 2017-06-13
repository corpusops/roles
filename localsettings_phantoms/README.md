# corpusops.roles/localsettings_phantoms ansible role
## Documentation
Needs to be applied before (next line should be on one line (parsed during tests)):
- cops roles dependencies: corpusops.roles/localsettings_profile

- This installs phantoms in `/opt` and links into your PATH (`/usr/local`)
- All the behavior can be tweaked by variables (`corpusops_localsettings_phantoms_`)

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/localsettings_phantoms_vars/role.yml
```

## installing hashicorp-phantoms from direct url(binaries)
```yaml
- hosts: all
  roles: [corpusops.roles/localsettings_phantoms]
  vars:
    corpusops_localsettings_phantoms_version: "7.10.0"
```
