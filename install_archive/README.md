# corpusops.roles/install_archive ansible role

## Documentation

- Download, unpack, Install an archive from a remote source
- It supports sha1, sha256 gpg or no-check tarball integrity checks
- The gpg key or the shas can be either a string or
  downloaded from a remote http location

### Dowload archives from remotes
```yaml
# most playbooks will want
# the "version" inline variable before including
# this tasks file
# EG:
- include_role: {name: corpusops.roles/install_archive}
  vars:
    archive:
      filetest: [bin/app]
      app_path: "/opt/app-{{item}}"
      urls:
        archive_crc: "https://app-{{item}}.shasums"
        archive: "http://app-{{item}}.tgz"
        verify_sha1: true
  with_items: [1.0, 2.0]

- include_role: {name: corpusops.roles/install_archive}
  vars:
    archive:
      filetest: [bin/app]
      app_path: "/opt/app-{{item}}"
      urls:
        archive_crc: "XXX_SuperHash0123456789"
        archive: "http://app-{{item}}.tgz"
        verify_sha1: true
  with_items: [1.0, 2.0]

- include_role: {name: corpusops.roles/install_archive}
  vars:
    archive:
      filetest: [bin/app]
      archive: "app-{{item}}.tgz"
      app_path: "/opt/app-{{item}}"
      urls:
        archive_crc: "https://app-{{item}}.shasums"
        archive: "http://app-{{item}}.tgz"
        verify_sha256: true
  with_items: [1.0, 2.0]

- include_role: {name: corpusops.roles/install_archive}
  vars:
    archive:
      filetest: [bin/app]
      app_path: "/opt/app-{{item}}"
      urls:
        archive_crc: "https://app.asc"
        archive: "http://app-{{item}}.tgz"
        verify_gpg: [9D41F3C3, http://goog.net/pub.key]
  with_items: [1.0, 2.0]
```

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/install_archive/role.yml \
    --tags=vars,corpusops_vars,corpusops_install_archive_vars
```
