# corpusops.roles/services_proxy_haproxy ansible role
## Documentation

- Installs haproxy on your host
- You may have a look to [haproxy_registrations](../haproxy_registration) role to configure additional haproxy objects
- Will automaticaly generate selfsigned certificate as main SSL cert if you did not configured ``corpusops_services_proxy_haproxy_maincert_crt`` (concatenate here crt, chain & key)

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/services_proxy_haproxy/role.yml \
   -t corpusops.roles/services_proxy_haproxy_vars
```
