# corpusops.roles/services_mail_postfix ansible role
## Documentation

- Installs postfix on your host, for vars see [related vars](../services_mail_postfix_vars)

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv \
    roles/corpusops.roles/services_mail_postfix_vars/role.yml
```
- [vars](https://github.com/corpusops/roles/blob/master/services_mail_postfix_vars/defaults/main.yml)


## postfix mode
- ``corpusops_services_mail_postfix_mode``: one of relay, catchall, custom<br/>
    preconfigure role options depending on the rule

    - relay: this server will be used only as a SMTP Relay.
    - catchall: set catchall address and virtual_alias_map
      to redirect everything to this address
    - localdeliveryonly: deliver only on localhost
    - custom: do not react to any preselected option


### SSL
(by default we use a selfsigned cert)
```yaml
corpusops_services_mail_postfix_cert: |-
    -----BEGIN CERTIFICATE-----
    -----END CERTIFICATE-----
corpusops_services_mail_postfix_cert_key: |-
    -----BEGIN RSA PRIVATE KEY-----
    -----END RSA PRIVATE KEY-----
```

### Relay example
```yaml
corpusops_services_mail_postfix_mode: relay
corpusops_services_mail_postfix_relay: mail.foo.com
corpusops_services_mail_postfix_relay_domains:
- foo.com: OK
```

### Catchall example
```yaml
corpusops_services_mail_postfix_mode: catchall
corpusops_services_mail_postfix_catchall: myuser@foo.com
```

### catchall with relay

```yaml
corpusops_services_mail_postfix_mode: catchall
corpusops_services_mail_postfix_catchall: myuser@foo.com
```

## Add to virtual alias map
```yaml
corpusops_services_mail_postfix_virtual_alias_map_custom:
- {'/.*/': "foobar.com"}
corpusops_services_mail_postfix_transport: "{{
  corpusops_services_mail_postfix_virtual_alias_map_custom +
  corpusops_services_mail_postfix_virtual_alias_map_default}}
```

## Authenticated relay
```yaml
corpusops_services_mail_postfix_sasl_passwd:
- entry: '[mail.foo.com]', user: "bar@foo.com", password: "xxx"
```


## Add to transport

```yaml
corpusops_services_mail_postfix_transport_custom:
corpusops_services_mail_postfix_transport: "{{
  corpusops_services_mail_postfix_transport_custom +
  corpusops_services_mail_postfix_transport_default}}
```

## restrictions
- See variables to see default smtpd_relay_restrictions, smtpd_recipient_restrictions, smtpd_client_restrictions, smtpd_sender_restrictions, smtpd_helo_restrictions.



## Example integration
```yaml
mail_sysadmin: "sysadmin+{{inventory_hostname}}@foo.com"
# mail_catchall: "{{mail_sysadmin}}"
mail_relay: mail.foo.com
mail_user: "too@foo.com"
mail_pwd: "secret"
mail_alias_map:
- "/root@.*/": "{{mail_sysadmin}}"
- "/postmaster@.*/": "{{mail_sysadmin}}"
- "/abuse@.*/": "{{mail_sysadmin}}"
- "/.*@{{inventory_hostname}}/": "{{mail_sysadmin}}"
- "/.*@localhost/": "{{mail_sysadmin}}"
- "/.*@.local/": "{{mail_sysadmin}}"
corpusops_services_mail_postfix_catchall: "{{mail_catchall|default('')}}"
corpusops_services_mail_postfix_mode: relay
corpusops_services_mail_postfix_sasl_passwd:
- {entry: "[{{mail_relay}}]", user: "{{mail_user}}", password: "{{mail_pwd}}"}
corpusops_services_mail_postfix_relay: "{{mail_relay}}"
corpusops_services_mail_postfix_virtual_alias_map_extra: "{{mail_alias_map}}"
```
