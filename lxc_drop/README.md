# corpusops.lxc_drop ansible role
## Documentation

Delete completly a lxc container from selected hosts if existing

## example use
```bash
ansible-playbook -l my_lxcs_host.foo.net  -vvv roles/corpusops.lxc_drop/role.yml \
        -e lxc_container_name=foo
```

