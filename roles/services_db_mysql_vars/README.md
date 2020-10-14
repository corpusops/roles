# corpusops.roles/services_db_mysql_vars variables role
## Documentation
- You may take a look to the
  [filter](./filter_plugins/copsf_mysql.py)
  that autotune mysql for you from various settings and the
  ``memory_usage_percent`` knob.

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv \
    roles/corpusops.roles/services_db_mysql_vars/role.yml
```
