# ssh key wrapper

Get or create (if `ssh_key_create` is true) a ssh key corresponding to relative infos.

Remember that the key will be generated on the `ssh_key_controller` host which defaults to `inventory_hostname`.

```yaml
# will create a /tmp/test/tutu ssh key
# please read ./defaults/main.yml for other options
- include_role: {name: corpusops.roles/ssh_key}
  vars:
    ssh_key_directory: /tmp/test
    ssh_key_name: tutu
```

Will set those variables:
    - `ssh_key_export`: community.crypto.openssh_keypair result
    - `ssh_key_priv`: private key file content
    - `ssh_key_pub`: public key file content

