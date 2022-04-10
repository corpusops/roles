# gpg key wrapper

Get or create (if `gpg_key_create` is true) a gpg key corresponding to relative infos.

'keynotpresent' will be in `gpg_key_idc.stdout` if key is missing

```yaml
- block:
  - include_role: {name: corpusops.roles/gpg_key}
  loop_control: {loop_var: keyinfo}
  loop:
  - name: "foo"
    email: "foo@foo.com"
    password: "secret"
```

Will set those variables:
    - `gpg_key_id`: key id

if `gpg_key_export is true`, those variables will also be exported:
    - `gpg_key`:  public key
    - `gpg_key_private`: private key

