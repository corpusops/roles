# corpusops.roles/lxc_register ansible role
## Documentation

Add dynamically a lxc container to the ansible inventory

## example use
```bash
ansible-playbook -l my_lxcs_host.foo.net  -vvv roles/corpusops.roles/lxc_register/role.yml \
        -e lxc_container_name=foo
```

You ll then be able in further execution of a playbook to refer ``foo`` in hosts and this will
execute in the context of that specific container.

## Example use in your playbooks
foo.yml
```yaml
- hosts: all
  roles: [corpusops.roles/lxc_register]

- hosts: "{{lxc_container_name}}"
  tasks:
      - shell: "hostname -f;ip addr show;whoami"
```

Then exec it
```bash
ansible-playbook -l my_lxcs_host.foo.net  -vvv foo.yml \
        -e lxc_container_name=foo
```


