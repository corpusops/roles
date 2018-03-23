# corpusops.roles/localsettings_certbot ansible role
## Documentation
Install the certbot package (and scripts (cron(not finished, waiting to integrate DNS01), & http challenge&)

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/localsettings_certbot/role.yml \
   -t corpusops.roles/localsettings_certbot_vars
```
