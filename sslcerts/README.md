# corpusops.roles/sslcerts ansible role
## Documentation
- Add ssl certs to /etc/ssl
- Add keys to /etc/ssl/private
- Add haproxy flavor (one file cert to haproxy path)
- see [./test.yml](./test.yml)
- see [./defaults/main.yml](./defaults/main.yml)


```yaml
- include_role: corpusops.roles/sslcerts
  vars:
     _cops_sslcerts:
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
