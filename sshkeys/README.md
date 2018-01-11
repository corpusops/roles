# corpusops.roles/sshkeys ansible role
## Documentation

- Add/Remove ssh public keys from authorized_keys files
- this is a thin wrapper to ansible [authorized_keys](http://docs.ansible.com/ansible/latest/authorized_key_module.html)
- see [./test.yml](./test.yml)
- see [./defaults/main.yml](./defaults/main.yml)


```yaml
- include_role: corpusops.roles/sshkeys
  vars:
     _cops_sshkeys:
        removed:
          root:
            # all:
            #   delete: for all users with a authorized_keys
            #   add: for all users with a valid home
            # null: only for user (key)
            mode: null / all
            ssh_keys:
            - key: "ssh-rsa xxxx"
            - key: "ssh-rsa xxxx"
              comment: foobar
              key_options: ""
        added:
          root:
            mode: null / all
            ssh_keys:
            - key: "ssh-rsa xxxx", remove_for_all: true
            - key: "ssh-rsa xxxx"
              path: "/foo/authorized_keys"
              manage_dir: false
              comment: foobar
              key_options: ""
```
