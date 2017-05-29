# corpusops.roles/localsettings_packer ansible role
## Documentation
Needs to be applied before (next line should be on one line (parsed during tests)):
- cops roles dependencies: corpusops.roles/localsettings_profile

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/localsettings_packer/role.yml \
   -t corpusops.roles/localsettings_packer_vars
```

## installing from packages
Its the default on Debian Alike
```yaml
- hosts: all
  roles: [corpusops.roles/localsettings_packer]
  vars:
    corpusops_localsettings_packer_version: 8
    corpusops_localsettings_packer_packages_default: ['packer-{v}', 'packer-{v}-packer', 'packer-{v}-src']
    corpusops_localsettings_packer_arch: amd64
```

## installing from direct url (binaries)
Its the default on Redhat Alike
```yaml
- hosts: all
  roles: [corpusops.roles/localsettings_packer]
  vars:
    corpusops_localsettings_packer_version: 1.7"
    corpusops_localsettings_packer_packages: []
```

## installing from direct url (binaries) - packer1.7
```yaml
- hosts: all
  roles: [corpusops.roles/localsettings_packer]
  vars:
    corpusops_localsettings_packer_version: "1.6"
    corpusops_localsettings_packer_packages: []
```

## installing from direct url -- custom
```yaml
- hosts: all
  roles: [corpusops.roles/localsettings_packer]
  vars:
    corpusops_localsettings_packer_version: myver
    corpusops_localsettings_jdk_urlmap:
      myver: 'https://storage.packerogleapis.com/packer/packer{v}.{f}.tar.gz'
    corpusops_localsettings_packer_packages: []
    corpusops_localsettings_packer_shas:
      packermyver-linux-amd64.tar.gz: "sha256:foobar"
```
