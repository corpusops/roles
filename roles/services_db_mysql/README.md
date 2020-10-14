# corpusops.roles/services_db_mysql ansible role
## Documentation

- Installs mysql on your host
- You may have a look to [mysql_vhost](../mysql_vhost) role to configure additional vhosts

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/services_db_mysql/role.yml \
   -t corpusops.roles/services_db_mysql_vars
```
