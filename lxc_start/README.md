# corpusops.lxc_start ansible role
## Documentation

Start completly a lxc container from selected hosts if existing

## example use
```bash
ansible-playbook -l my_lxcs_host.foo.net  -vvv roles/corpusops.roles/lxc_start/role.yml \
        -e lxc_container_name=foo
```

