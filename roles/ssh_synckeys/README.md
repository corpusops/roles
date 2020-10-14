# corpusops.roles/ssh_synckeys ansible role
## Documentation

- Sync one user authorized_keys from anothers users on the same system



```yaml
- include_role: corpusops.roles/ssh_synckeys
  vars:
    _cops_ssh_synckeys:
      users: [foobar]
      to_user: muche

```
