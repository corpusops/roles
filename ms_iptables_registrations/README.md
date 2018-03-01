# corpusops.roles/ms_iptables_registrations ansible role
## Documentation
Managment of ms_iptables objects

Search all ``corpusops_ms_iptables_registrations_registrations_<foo>`` vars in variables to merged 
them to construct the final configuration

- see [filter plugin](../ansible_plugins/filter_plugins/copsf_ms_iptables.py)
- see [ms_iptables_server role vars](../services_firewall_ms_iptables_vars)
- see [ms_iptables_server role](../services_firewall_ms_iptables)
- see [defaults](./defaults/main.yml)
- see [template](./templates/cfg.json)
- see [tests](./test.yml)

### Configure ms_iptables objects
- tasks/main.yml
    ```yaml
    - include_role: {name: corpusops.roles/ms_iptables_registrations}
      vars:
        _corpusops_ms_iptables_registrations:   
            load_default_rules: bool
            load_default_flush_rules: bool
            load_default_hard_policies: bool
            load_default_open_policies: bool
            ipv6: bool
            # rules are basically shell commands (like iptables calls)
            policy: string (hard/open)
            hard_policies: list of rules to enforce firewall
            open_policies: list of rules for having an open firewall (non strict mode)
            rules: list of rules to apply to the firewall
            flush_rules: list of custom rules to flush firewall
```

#### Exemple

```yaml
corpusops_ms_iptables_registrations_registrations_foo:
  rules:
  - iptables -w -t filter -A INPUT -i lxcbr1 -p udp -m udp --dport 67 -j ACCEPT
```
