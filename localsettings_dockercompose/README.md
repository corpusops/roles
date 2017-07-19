# corpusops.roles/localsettings_dockercompose ansible role
## Documentation
Needs to be applied before (next line should be on one line (parsed during tests)):
- cops roles dependencies: corpusops.roles/localsettings_profile

- This installs dockercompose in `/opt` and links into your PATH (`/usr/local`)
- All the behavior can be tweaked by variables (`corpusops_localsettings_dockercompose_`)

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/localsettings_dockercompose_vars/role.yml
```

## installing hashicorp-dockercompose from direct url(binaries)
```yaml
- hosts: all
  roles: [corpusops.roles/localsettings_dockercompose]
  vars:
    corpusops_localsettings_dockercompose_version: "1.0.0"
```
