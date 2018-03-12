# corpusops.roles/services_db_mysql_role ansible role
## Documentation

- Create/modify users in mysql server
- Wrapper around [postgres_user ansible module](http://docs.ansible.com/ansible/latest/mysql_user_module.html)
- see [./test.yml](./test.yml)
- see [./defaults/main.yml](./defaults/main.yml)

```yaml
- include_role: { name: corpusops.roles/mysql_role}
  vars:
    _cops_mysql_role:
      name: "mysql_role_udb3_user"
      host: '*'
      db: "mysql_role_udb2"
      password: verysecret
      priv: "mysql_role_udb2.*:ALL"
```
