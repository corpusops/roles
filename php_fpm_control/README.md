# corpusops.roles/php_fpm_control ansible role

## Documentation

Managment of php_fpm service.

### usage

- see [test](./test.yml)

```yaml
- hosts: all
  roles:
    - {role: corpusops.roles/php_fpm_control}
  vars:
      _corpusops_php_fpm_control:
        install: false
        basename: myvhost
```


## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/php_fpm_control/role.yml \
    --tags=vars,corpusops_vars,corpusops_php_fpm_control_vars
```
