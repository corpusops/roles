# corpusops.roles/get_secret_variable ansible role
## Documentation
- Generate a token (secret) on the remote host if not existing
  else return the value (remote version of lookup(password)

```yaml
- include_role: {name: corpusops.roles/get_secret_variable}
  vars:
    _cops_get_secret_variable:
      name: name of the token
      path: path to a directory that will stock it (/etc/secrets)
      length: length of the token to generate (32)

```

Exemple:
```yaml
- include_role: {name: corpusops.roles/get_secret_variable}
  vars:
    _cops_get_secret_variable:
      name: my_token
      path: /etc/secrets
- debug: {msg: "{{my_token}}"}
```
