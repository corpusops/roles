# corpusops.roles/set_alternatives ansible role

## Documentation

- Setup the linux alternative system and link one version on the system

### Install alternatives
- main target entry is mandatory and designate the current alternative
- each "bins" entry represents an alternative to be defined
- Be warn, all existing alternatives are removed before the entries to be defined

vhost
```yaml
- include_role: {name: corpusops.roles/set_alternatives}
  vars:
    version: "1.0"
    alternatives:
      mybin:
        target: "/usr/bin/fii"
        bins:
          - onefii:
              target: "/opt/apps/fii-{{version}}/bin/fii"
```

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/set_alternatives/role.yml \
    --tags=vars,corpusops_vars,corpusops_set_alternatives_vars
```
