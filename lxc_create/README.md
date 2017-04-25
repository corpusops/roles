# corpusops.lxc_create ansible role
## Documentation

Create  lxc container

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.lxc_vars/role.yml \
   -t corpusops.lxc_vars
```

## Example
You may better use though corpusops.bootstrap via [this playbook](https://github.com/corpusops/playbooks/blob/master/provision/lxc_container.yml)

```
cd /srv/corpusops/corpusops.bootstrap
bin/ansible-playbook playbooks/corpusops/provision/lxc_container.yml -l myhost -e "lxc_container_name=foo"
```

If you want to only execute this role
```
bin/ansible-playbook roles/corpusops.lxc_create/role.yml -l myhost -e "lxc_container_name=foo"
```

You can add the ``from_container`` argument to initialise from a stopped but already existing container.
```
bin/ansible-playbook roles/corpusops.lxc_create/role.yml -l myhost -e "lxc_container_name=foo from_container=mytemplate"
```

Create a lxc on top of another one via overlayfs:
```
bin/ansible-playbook roles/corpusops.lxc_create/role.yml -l myhost -e "lxc_container_name=foo from_container=bar corpusops_lxc_backing_store=overlayfs"
```

