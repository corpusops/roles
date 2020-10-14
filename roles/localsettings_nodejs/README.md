# corpusops.roles/localsettings_nodejs ansible role
## Documentation
Needs to be applied before (next line should be on one line (parsed during tests)):
- cops roles dependencies: corpusops.roles/localsettings_profile

- This installs nodejs in `/opt` and links into your PATH (`/usr/local`)
- All the behavior can be tweaked by variables (`corpusops_localsettings_nodejs_`)

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/localsettings_nodejs_vars/role.yml
```

## installing hashicorp-nodejs from direct url(binaries)
```yaml
- hosts: all
  roles: [corpusops.roles/localsettings_nodejs]
  vars:
    corpusops_localsettings_nodejs_version: "7.10.0"
```
