# corpusops.localsettings_jdk ansible role
## Documentation
Needs to be applied before (next line should be on one line (parsed during tests)):
- cops roles dependencies: corpusops.roles/localsettings_profile

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/localsettings_jdk/role.yml \
   -t corpusops.localsettings_jdk_vars
```

## installing from packages
Its the default on Debian Alike
```yaml
- hosts: all
  roles: [corpusops.localsettings_jdk]
  vars:
    corpusops_localsettings_jdk_version: 8
    corpusops_localsettings_jdk_packages: ['java-pkg']
    corpusops_localsettings_jdk_arch: amd64
```

## installing from direct url (binaries)
Its the default on Redhat Alike
```yaml
- hosts: all
  roles: [corpusops.localsettings_jdk]
  vars:
    corpusops_localsettings_jdk_version: 8u112
    corpusops_localsettings_jdk_packages: []
```

## installing from direct url (binaries) - jdk1.7
```yaml
- hosts: all
  roles: [corpusops.localsettings_jdk]
  vars:
    corpusops_localsettings_jdk_version: 7u80
    corpusops_localsettings_jdk_packages: []
```

## installing from direct url -- custom
```yaml
- hosts: all
  roles: [corpusops.localsettings_jdk]
  vars:
    corpusops_localsettings_jdk_version: myver
    corpusops_localsettings_jdk_urlmap:
      8u112: 'http://download.oracle.com/otn-pub/java/jdk/{v}-b15/jdk-{v}-linux-{arch}.tar.gz'
    corpusops_localsettings_jdk_packages: []
    corpusops_localsettings_jdk_shas:
      jdk-myveru80-linux-x64.tar.gz: "sha256:foobar"
```
