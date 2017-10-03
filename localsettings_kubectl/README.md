# corpusops.roles/localsettings_kubectl ansible role
## Documentation
Needs to be applied before (next line should be on one line (parsed during tests)):
- cops roles dependencies: corpusops.roles/localsettings_profile

- This installs kubectl in `/opt` and links into your PATH (`/usr/local`)
- All the behavior can be tweaked by variables (`corpusops_localsettings_kubectl_`)

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/localsettings_kubectl_vars/role.yml
```

## installing hashicorp-kubectl from direct url(binaries)
```yaml
- hosts: all
  roles: [corpusops.roles/localsettings_kubectl]
  vars:
    corpusops_localsettings_kubectl_version: "1.0.0"
```
