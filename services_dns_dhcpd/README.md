# corpusops.roles/services_dns_dhcpd ansible role
## Documentation

Installs dhcpd on your host

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/services_dns_dhcpd/role.yml \
   -t corpusops.roles/services_dns_dhcpd_vars
```


``` yaml
 dhcp_servers:
  hosts: {onehost.mydomain.lan: {}}
  vars:
    lan_ips: {
      'onehost.mydomain.lan': ["10.55.0.2"],
    }
    corpusops_services_dns_dhcpd_interfaces: "brlan"
    corpusops_services_dns_dhcpd_conf_custom:
        domain_name_servers: "10.55.0.1"
        domain_name: mydomain.lan
    corpusops_services_dns_dhcpd_subnets:
        10.55.0.0:
          netmask: 255.255.248.0
          conf:
            'range': '10.55.4.1 10.55.15.253'
            'option routers': '10.55.0.1'
            'option domain-name': '"mydomain.lan"'
            'option domain-name-servers': '10.55.0.1'
    corpusops_services_dns_dhcpd_hosts:
        onehost.mydomain.lan:
          'hardware ethernet': 'aa:aa:aa:aa:aa:aa'
          'fixed-address': 'onehost.mydomain.lan'
```



