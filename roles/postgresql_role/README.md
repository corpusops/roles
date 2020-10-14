# corpusops.roles/services_db_postgresql_role ansible role
## Documentation

- Create/modify users in postgresql server
- Wrapper around [postgres_user ansible module](http://docs.ansible.com/ansible/latest/postgresql_user_module.html)
- see [./test.yml](./test.yml)
- see [./defaults/main.yml](./defaults/main.yml)

```yaml
- include_role:
    name: corpusops.roles/postgresql_role
  vars:
    _cops_postgresql_role:
      name: "postgresql_role_udb3_user"
      db: "postgresql_role_udb2"
      password: verysecret
```
