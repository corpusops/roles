
# utility to transfer lxc

## from one machine to same
```sh
$COPS_ROOT/bin/ansible-playbook -Dvvvv -i $inv lxc_teleport/do.yml -e "{lxc: lxc1, olxc: lxc2, bm: foo.bar.corp, dryrun: true}"
--skip-tags ssh_setup,rsync,reconfig_cfg,reconfig_rootfs,reconfig_postfix,reconfig_ssh,reconfig_bm,reconfig_lxc
```

## to remote host
```sh
$COPS_ROOT/bin/ansible-playbook -Dvvvv -i $inv    lxc_teleport/do.yml -e\
"{lxc: another-mylxc.bar.corp, olxc: intranet.bar.corp, bm: ovh-g2-8.bar.corp, obm: ovh-g2-9.bar.corp, dryrun: true}"  \
--skip-tags ssh_setup,rsync,reconfig_cfg,reconfig_rootfs,reconfig_postfix,reconfig_ssh,reconfig_bm,reconfig_lxc
```
