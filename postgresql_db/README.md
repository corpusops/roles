# corpusops.roles/services_db_postgresql_db ansible role
## Documentation

- Create a postgres database
- Wrapper around [postgres_db ansible module](http://docs.ansible.com/ansible/latest/postgresql_db_module.html)
- see [./test.yml](./test.yml)
- see [./defaults/main.yml](./defaults/main.yml)

```yaml
- include_role:
    name: corpusops.roles/postgresql_db
  vars:
    _cops_postgresql_db:
      db: "db1"
- include_role:
    name: corpusops.roles/postgresql_db
  vars:
    _cops_postgresql_db:
      db: "db2"
      template: "db1"
- include_role:
    name: corpusops.roles/postgresql_db
  vars:
    _cops_postgresql_db:
      db: "db1"
      become: false
      login_host: foobar
      login_user: "test"
      login_password: "secret"
```
