# corpusops.roles/postgresql_extensions ansible role
## Documentation

- Install extensions in the desired database
- Wrapper around [postgres_ex ansible module](http://docs.ansible.com/ansible/latest/postgresql_ext_module.html)
- see [./test.yml](./test.yml)
- see [./defaults/main.yml](./defaults/main.yml)

```yaml
- include_role:
    name: corpusops.roles/postgresql_extensions
  vars:
    _cops_postgresql_extensions:
      extensions: [fuzzystrmatch]
      db: "db1"
- include_role:
    name: corpusops.roles/postgresql_extensions
  vars:
    _cops_postgresql_extensions:
      extensions: [fuzzystrmatch]
      db: "db1"
      become: false
      login_host: foobar
      login_user: "test"
      login_password: "secret"

```
