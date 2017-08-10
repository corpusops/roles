# corpusops.roles/set_alternatives ansible role

## Documentation

- Setup the linux alternative system and link one version on the system

### Install a vhost
```yaml
- include_role: {name: corpusops.roles/set_alternatives}
  vars:
    version: "1.0"
    alternatives:
      mybin:
        target: "/usr/bin/fii"
        bins:
          - manualfii:
              target: "/opt/apps/fii-{{version}}/bin/fii"
```

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/set_alternatives/role.yml \
    --tags=vars,corpusops_vars,corpusops_set_alternatives_vars
```
