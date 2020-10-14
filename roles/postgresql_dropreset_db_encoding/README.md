# corpusops.roles/services_db_postgresql_dropreset_db_encoding ansible role
## Documentation

- Drop and recreate database if encoding is not correct
- see [test.yml](test.yml)

```yaml
- include_role:
    name: corpusops.roles/postgresql_dropreset_db_encoding
  vars:
    _cops_postgresql_drop_reset_db_encoding:
      db: "postgresql_dropreset_db_encoding_db1"
      version: "9.5"
      locale: "fr_FR.utf-8"
      encoding: "utf-8"
```
