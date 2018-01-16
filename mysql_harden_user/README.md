# corpusops.roles/services_db_mysql_harden_user ansible role
## Documentation

- Ensure root user is password protected
  if a password is set
- see [test.yml](test.yml)

```yaml
- include_role:
    name: corpusops.roles/mysql_harden_user
```
