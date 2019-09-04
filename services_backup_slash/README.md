# corpusops.roles/services_backup_slash ansible role
## Documentation

- backup all mounted partitions exept filtered ones (see variables)
  to one location on your filesystem with rsync.

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/services_backup_slash/role.yml \
   -t corpusops.roles/services_backup_slash_vars
```
