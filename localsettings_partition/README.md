# corpusops.roles/localsettings_partition ansible role
## Documentation

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/localsettings_partition/role.yml \
   -t corpusops.roles/localsettings_partition_vars
```

```yaml
# eg
corpusops_localsettings_partition_profile: "{{corpusops_localsettings_partition_profiles.stor1_stock}}"
```


A profile looks like (each part can be commited (and the corresponding conf will be then skipped; see role vars for examples)):

```yaml
corpusops_localsettings_partition_profiles:
  stor1_stock:
    raid:
    - {name: md2, level: "10", members: [/dev/sda2, /dev/sdb2]}
    lvm_pvs:
    - {name: md2, members: /dev/md2}
    lvm_vgs:
    - {name: vg, members: /dev/md2}
    lvm_lvs:
    - {name: data, lv_create_args: "-l +100%FREE"}
    fstab:
    - {name: /dev/vg/data, dest: /srv}
```
