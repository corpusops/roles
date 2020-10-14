# corpusops.roles/services_db_postgresql_privs ansible role
## Documentation

- Modify (GRANT/REVOKE) privileges for roles  in postgresql server
- Wrapper around [postgres_privs ansible module](http://docs.ansible.com/ansible/latest/postgresql_privs_module.html)
- see [./test.yml](./test.yml)
- see [./defaults/main.yml](./defaults/main.yml)

```yaml
- include_role:
    name: corpusops.roles/postgresql_privs
  vars:
    _cops_postgresql_privs:
      roles: "postgresql_privs_uprivdb3_user"
      database: "postgresql_privs_uprivdb2"
      type: database
      privs: ALL
```
