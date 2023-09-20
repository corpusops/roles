# corpusops.roles/services_dns_dhcpd6 ansible role
## Documentation

Installs dhcpd on your host

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/services_dns_dhcpd6/role.yml \
   -t corpusops.roles/services_dns_dhcpd6_vars
```


``` yaml
 dhcp_servers:
  hosts: {onehost.mydomain.lan: {}}
  vars:
    lan_ip6s: {
      'onehost.mydomain.lan': ["1234:554:443e:4565::2"],
    }
    corpusops_services_dns_dhcpd6_interfaces: "brlan"
    corpusops_services_dns_dhcpd6_conf_custom:
          domain_name_servers: "1234:554:443e:4565::2"
          domain_name: mydomain.lan
    corpusops_services_dns_dhcpd6_subnets:
          "1234:554:443e:4565::":
            netmask: 64
            conf:
              'range6': '1234:554:443e:4565:0:0:0:aaaa 1234:554:443e:4565:0:0:0:ffff'
              'option dhcp6.domain-search': '"mydomain.lan"'
              'option dhcp6.name-servers': '1234:554:443e:4565:0:0:0:2'
              # 'option routers': '1234:554:443e:4565::2'
    corpusops_services_dns_dhcpd6_hosts:
          onehost.mydomain.lan:
            'fixed-address6': "{{lan_ip6s['onehost.mydomain.lan'][0]}}"
            'host-identifier': 'option dhcp6.client-id 0:0:0:0:0:0:0'
```



