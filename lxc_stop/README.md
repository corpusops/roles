# corpusops.roles/lxc_stop ansible role
## Documentation

Stop completly a lxc container from selected hosts if existing

## example use
```bash
ansible-playbook -l my_lxcs_host.foo.net  -vvv roles/corpusops.roles/lxc_stop/role.yml \
        -e lxc_container_name=foo
```

