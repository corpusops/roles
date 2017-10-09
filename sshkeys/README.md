# corpusops.roles/sshkeys ansible role
## Documentation

- Add/Remove ssh public keys from authorized_keys files
- this is a thin wrapper to ansible [authorized_keys](http://docs.ansible.com/ansible/latest/authorized_key_module.html)
- see [./test.yml](./test.yml)
- see [./defaults/main.yml](./defaults/main.yml)


```yaml
- include_role: corpusops.roles/sshkeys
  vars:
    cops_sshkeys_removed:
      root:
        - key: "ssh-rsa xxxx"
        - key: "ssh-rsa xxxx"
          comment: foobar
          key_options: ""
    cops_sshkeys_added:
      root:
        - key: "ssh-rsa xxxx"
        - key: "ssh-rsa xxxx"
          path: "/foo/authorized_keys"
          manage_dir: false
          comment: foobar
          key_options: ""
```
