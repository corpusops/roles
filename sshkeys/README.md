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

Another dynamic sample

```yaml
corpusops_ssh_keys_map:
  baruser:
    - "ssh-rsa xx== far@user"
  foouser:
    - "ssh-rsa xx== foo@user"
  foouser2:
    - "ssh-rsa xx== foo@user2"
corpusops_ssh_added_keys_map_: |-
  {%- set admin_access = ["foouser"] %
  {%- set sadmin_access = ', '.join(admin_access) %}
  corp.foo.net: [{{sadmin_access}}]
  corp.foo.net: [foouser, foouser2]
corpusops_ssh_added_keys_map: "{{(corpusops_ssh_added_keys_map_
        |from_yaml|to_json).strip()}}"
corpusops_ssh_removed_keys_map:
  default: []
  other.foo.net: [baruser]
_cops_sshkeys:
  removed: |-
    {% set keys = [] %}
    {% set dkeys = {'root': {'mode': 'all', 'ssh_keys': keys}} %}
    {% set d = corpusops_ssh_removed_keys_map.get('default', []) %}
    {% for i in corpusops_ssh_removed_keys_map.get(ansible_host,
        corpusops_ssh_removed_keys_map.get(inventory_hostname, d)) %}
    {%  for j in corpusops_ssh_keys_map.get(i, []) %}
    {%    set _ = keys.append({'key': j}) %}
    {%  endfor %}
    {% endfor %}
    {{ dkeys | to_json }}
  added: |-
    {% set keys = [] %}
    {% set dkeys = {'root': {'ssh_keys': keys}} %}
    {% set d = corpusops_ssh_added_keys_map.get('default', []) %}
    {% for i in corpusops_ssh_added_keys_map.get(ansible_host,
          corpusops_ssh_added_keys_map.get(inventory_hostname, d)) %}
    {%  for j in corpusops_ssh_keys_map.get(i, []) %}
    {%    set _ = keys.append({'key': j}) %}
    {%  endfor %}
    {% endfor %}
    {{ dkeys | to_json }}
```
