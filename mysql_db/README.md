# corpusops.roles/services_db_mysql_db ansible role
## Documentation

- Create a mysql database
- Wrapper around [postgres_db ansible module](http://docs.ansible.com/ansible/latest/mysql_db_module.html)
- see [./test.yml](./test.yml)
- see [./defaults/main.yml](./defaults/main.yml)

```yaml
- include_role:
    name: corpusops.roles/mysql_db
  vars:
    _cops_mysql_db:
      db: "db1"
- include_role:
    name: corpusops.roles/mysql_db
  vars:
    _cops_mysql_db:
      db: "db2"
      template: "db1"
- include_role:
    name: corpusops.roles/mysql_db
  vars:
    _cops_mysql_db:
      db: "db1"
      become: false
      login_host: foobar
      login_user: "test"
      login_password: "secret"
```
