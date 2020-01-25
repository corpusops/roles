# domainops.roles/localsettings_certbot ansible role
## Documentation
Install the certbot package (and scripts (cron(not finished, waiting to integrate DNS01), & http challenge&)

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/domainops.roles/localsettings_certbot/role.yml \
   -t domainops.roles/localsettings_certbot_vars
```


## HTTP example
```yaml
---
letsencrypt:
  children:
    mygrp:
  vars:
    domainops_localsettings_certbot_test: false
    # To activate certbot renewal script (in cron)
    domainops_localsettings_certbot_has_cron: true
    domainops_localsettings_certbot_http: true
    # To activate haproxy certs installer in cron
    domainops_localsettings_certbot_haproxy: true
    domainops_localsettings_certbot_mailto: "sysadmin@mysuper-domain.com"
    domainops_localsettings_certbot_email: "{{domainops_localsettings_certbot_mailto}}"
letsencryptconsumer:
  vars:
    domainops_localsettings_certbot_domains: |-
      {%- set r = [ansible_fqdn] %}
      {%- for i in groups.get(inventory_hostname+'_lxcs', []) %}
      {%-   set idata = hostvars[i] %}
      {%-   set _ = r.extend(
              idata.get('certbot_domains',
                idata.get('haproxy_hosts', [])))%}
      {%- endfor %}
      {%- set _ = r.extend(
                    hostvars[inventory_hostname].get(
                      'certbot_domains', [])) %}
      {{- r | copsf_uniquify
            | copsf_refilter('mycompany-?domain.(net|fr|com|org|eu)', flags='XM',
                             whitelist='((mysuper-?domain.(com|fr|org|eu))$|((fr|formations).mysuper-?domain.net))')
            | to_json }}

```


## DNS example with OVH
```yaml
---
letsencrypt:
  children:
    mygrp:
  vars:
    domainops_localsettings_certbot_test: false
    # To activate certbot renewal script (in cron)
    domainops_localsettings_certbot_has_cron: true
    domainops_localsettings_certbot_http: false
    # To activate haproxy certs installer in cron
    domainops_localsettings_certbot_dns: true
    domainops_localsettings_certbot_dns_force_workers_restart: false/true
    domainops_localsettings_certbot_mailto: "sysadmin@mysuper-domain.com"
    domainops_localsettings_certbot_email: "{{domainops_localsettings_certbot_mailto}}"
    domainops_localsettings_certbot_dns_ovh_application_key: xx
    domainops_localsettings_certbot_dns_ovh_application_secret: yy
    domainops_localsettings_certbot_dns_ovh_consumer_key: zz
letsencryptconsumer:
  vars:
    domainops_localsettings_certbot_domains: |-
      {%- set r = [ansible_fqdn] %}
      {%- for i in groups.get(inventory_hostname+'_lxcs', []) %}
      {%-   set idata = hostvars[i] %}
      {%-   set _ = r.extend(
              idata.get('certbot_domains',
                idata.get('haproxy_hosts', [])))%}
      {%- endfor %}
      {%- set _ = r.extend(
                    hostvars[inventory_hostname].get(
                      'certbot_domains', [])) %}
      {{- r | copsf_uniquify
            | copsf_refilter('mycompany-?domain.(net|fr|com|org|eu)', flags='XM',
                             whitelist='((mysuper-?domain.(com|fr|org|eu))$|((fr|formations|m).mysuper-?domain.net))')
            | to_json }}

```
# vim: set ft=sls:
