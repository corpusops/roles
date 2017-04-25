# corpusops.roles/lxc_sshauth ansible role
## Documentation

Add ssh keys to the root user of a lxc container to allow
external users to connect to

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/lxc_vars/role.yml
```

## Notes
Basically, you ll want in your inventory:

To configure globally:
<pre>
corpusops_lxc_ssh_keys: ["ssh-rsa AAAAB..== xx@foo"]
corpusops_lxc_ssh_keys_paths: ["/tmp/foo.pub"]
</pre>


To override for a specific container:
<pre>
corpusops_lxc_containers_mycontainer:
  ssh_keys: ["ssh-rsa AAAAB..== xx@foo"]
  ssh_keys_paths: ["/tmp/foo.pub"]
</pre>


## Example use
Configure your inventory (see above)
and to apply

```bash
ansible-playbook -l my_lxcs_host.foo.net  -vvv roles/corpusops.roles/lxc_sshauth/role.yml \
   -e lxc_container_name=foo
``` 
