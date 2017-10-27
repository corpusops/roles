# corpusops.roles/nginx_control ansible role

## Documentation

Managment of nginx service.

### usage

- see [test](./test.yml)

```yaml
- hosts: all
  roles:
    - {role: corpusops.roles/nginx_control}
  vars:
      _corpusops_nginx_control:
        install: false
        basename: myvhost
```


## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/nginx_control/role.yml \
    --tags=vars,corpusops_vars,corpusops_nginx_control_vars
```
