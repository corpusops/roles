# corpusops.roles/lxc_register ansible role
## Documentation

Remove some password entries from the container passwd database.

(EG: To secure root & ubuntu from any password)

## example use
```bash
ansible-playbook -l my_lxcs_host.foo.net  -vvv roles/corpusops.roles/lxc_remove_password/role.yml \
        -e lxc_container_name=foo
```
