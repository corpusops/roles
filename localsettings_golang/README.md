# corpusops.localsettings_golang ansible role
## Documentation
Needs to be applied before (next line should be on one line (parsed during tests)):
- cops roles dependencies: corpusops.roles/localsettings_profile

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/localsettings_golang/role.yml \
   -t corpusops.localsettings_golang_vars
```

## installing from packages
Its the default on Debian Alike
```yaml
- hosts: all
  roles: [corpusops.localsettings_golang]
  vars:
    corpusops_localsettings_golang_version: 8
    corpusops_localsettings_golang_packages_default: ['golang-{v}', 'golang-{v}-go', 'golang-{v}-src']
    corpusops_localsettings_golang_arch: amd64
```

## installing from direct url (binaries)
Its the default on Redhat Alike
```yaml
- hosts: all
  roles: [corpusops.localsettings_golang]
  vars:
    corpusops_localsettings_golang_version: 1.7"
    corpusops_localsettings_golang_packages: []
```

## installing from direct url (binaries) - golang1.7
```yaml
- hosts: all
  roles: [corpusops.localsettings_golang]
  vars:
    corpusops_localsettings_golang_version: "1.6"
    corpusops_localsettings_golang_packages: []
```

## installing from direct url -- custom
```yaml
- hosts: all
  roles: [corpusops.localsettings_golang]
  vars:
    corpusops_localsettings_golang_version: myver
    corpusops_localsettings_jdk_urlmap:
      myver: 'https://storage.googleapis.com/golang/go{v}.{f}.tar.gz'
    corpusops_localsettings_golang_packages: []
    corpusops_localsettings_golang_shas:
      golangmyver-linux-amd64.tar.gz: "sha256:foobar"
```
