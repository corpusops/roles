# corpusops.roles/get_secret_variable ansible role
## Documentation

- Sync one user authorized_keys from anothers users on the same system



```yaml
- include_role: corpusops.roles/get_secret_variable
  vars:
    _cops_get_secret_variable:
      users: [foobar]
      to_user: muche

```
