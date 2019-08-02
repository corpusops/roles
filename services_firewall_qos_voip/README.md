# corpusops.roles/services_firewall_qos_voip ansible role
## Documentation

- Installs qos_voip on your host
- This script use TC and IP(6)TABLES to shape internet trafic on your router
- Please read [the script](./templates/etc/init.d/qos_voip) comments to understand what's under the hood

## Example configurations
```yaml
corpusops_services_firewall_qos_voip_defaults_qos_if: "brnet"
corpusops_services_firewall_qos_voip_defaults_ingress_speed: "{{85*1024}}"
corpusops_services_firewall_qos_voip_defaults_egress_speed: "{{900*1024}}"
corpusops_services_firewall_qos_voip_defaults_dry_run: ""
```

```yaml
corpusops_services_firewall_qos_voip_defaults_use_lsb: ""
corpusops_services_firewall_qos_voip_defaults_dry_run: ""
corpusops_services_firewall_qos_voip_defaults_sdebug: ""
corpusops_services_firewall_qos_voip_defaults_debug: "1"
corpusops_services_firewall_qos_voip_defaults_qos_if: "eth0"
corpusops_services_firewall_qos_voip_defaults_voip_ifs: "eth0"
corpusops_services_firewall_qos_voip_defaults_ingress_speed: "$((80*1024))"
corpusops_services_firewall_qos_voip_defaults_egress_speed: "$((800*1024))"
corpusops_services_firewall_qos_voip_defaults_voip_egress_rate: "$((4096*2))"
corpusops_services_firewall_qos_voip_defaults_voip_ingress_rate: "4096"
acorpusops_services_firewall_qos_voip_defaults_extra: |-
  VOIP_EGRESS_CEIL="$VOIP_EGRESS_RATE"
  VOIP_INGRESS_CEIL="$VOIP_INGRESS_RATE"
corpusops_services_firewall_qos_voip_dry_run: ''
```

```yaml
corpusops_services_firewall_qos_voip_defaults_qos_if: "brnet"
corpusops_services_firewall_qos_voip_defaults_ingress_speed: "{{85*1024}}"
corpusops_services_firewall_qos_voip_defaults_egress_speed: "{{900*1024}}"
corpusops_services_firewall_qos_voip_defaults_dry_run: ""
```

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/services_firewall_qos_voip/role.yml \
   -t corpusops.roles/services_firewall_qos_voip_vars
```
