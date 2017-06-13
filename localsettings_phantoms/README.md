# corpusops.roles/localsettings_phantoms ansible role
## Documentation
Needs to be applied before (next line should be on one line (parsed during tests)):
- cops roles dependencies: corpusops.roles/localsettings_profile

- This installs phantomjs & casperjs in `/opt` and links into your PATH (`/usr/local`)
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
    corpusops_localsettings_phantoms_phantomjs_version: '2.1.1'
    corpusops_localsettings_phantoms_phantomjs_sha: '86dd9a4bf4aee45f1a84c9f61cf1947c1d6dce9b9e8d2a907105da7852460d2f'
    corpusops_localsettings_phantoms_casperjs_version: '1.1.3'
```
