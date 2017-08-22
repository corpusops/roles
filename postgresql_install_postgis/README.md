# corpusops.roles/postgresql_install_postgis ansible role
## Documentation

- Install postgis in the desired database
- see [./test.yml](./test.yml)

```yaml
- include_role:
    name: corpusops.roles/postgresql_install_postgis
  vars:
    _cops_postgresql_install_postgis:
      db: "db1"
- include_role:
    name: corpusops.roles/postgresql_install_postgis
  vars:
    _cops_postgresql_install_postgis:
      db: "db1"
      become: false
      login_host: foobar
      login_user: "test"
      login_password: "secret"

```
