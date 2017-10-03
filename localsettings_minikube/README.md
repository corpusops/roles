# corpusops.roles/localsettings_minikube ansible role
## Documentation
Needs to be applied before (next line should be on one line (parsed during tests)):
- cops roles dependencies: corpusops.roles/localsettings_profile

- This installs minikube in `/opt` and links into your PATH (`/usr/local`)
- All the behavior can be tweaked by variables (`corpusops_localsettings_minikube_`)

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/localsettings_minikube_vars/role.yml
```

## installing hashicorp-minikube from direct url(binaries)
```yaml
- hosts: all
  roles: [corpusops.roles/localsettings_minikube]
  vars:
    corpusops_localsettings_minikube_version: "1.0.0"
```
