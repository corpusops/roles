# corpusops.roles/services_firewall_fail2ban ansible role
## Documentation

- Installs fail2ban on your host
- You may have a look to [fail2ban_vhost](../fail2ban_vhost) role to configure additional vhosts

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/services_firewall_fail2ban/role.yml \
   -t corpusops.roles/services_firewall_fail2ban_vars
```
