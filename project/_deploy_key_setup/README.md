# Helper to deploy ssh keys during deployment
- This enables you to put ssh keys inside  your inventory and bring them back to your filesystem (in the later examples: inside ``./local/.ssh``) for ansible to be able to consume them for connecting to remote envs.
- This is very useful in CI setups when you spin containers to deploy remotly or even to ship your deploy code (keys crypted in a vault) inside your central repository embracing InfrastructureASCode principles.

- The worklow is:
    - to set the ``cops_deploy_ssh_key_paths`` that contains all the ssh keys you ll have to use
    - Then to run this role to deploy them
    - Then to reffer them inside the inventory for ansible to use them as the key used during SSH authentication.


## Anatomy of the cops_deploy_ssh_key_paths

- First, setup in your inventory the ``cops_deploy_ssh_key_paths`` variable
  (inside a var file)


```yaml
# should be in an encypted vault
cops_deploy_ssh_key_paths:
  deploy:
    path: "{{'local/.ssh/deploy_key'|copsf_abspath}}"
    pub: >-
         ssh-rsa xxx x@y
    private: |-
             -----BEGIN RSA PRIVATE KEY-----
             -----END RSA PRIVATE KEY-----
```

- Then you can reference the ssh keyfile in the hosts configs inside the inventorya

    ```ini
    localhost ansible_connection=local
    staging-myapp.foo.net  sudo_flags=-HE ansible_port=22 ansible_user=root ansible_ssh_common_args="-i {{cops_deploy_ssh_key_paths['deploy'].path}}"
    # if interactive sudo pw
    # staging-myapp.foo.net sudo_flags=-SHE ansible_port=22 ansible_user=root ansible_ssh_common_args="-i {{cops_deploy_ssh_key_paths['deploy'].path}}"
     ```

## Call the role

- Execute such a playbook

    ```yaml
    # should be in an encypted vault
    - hosts: localhost
      # for the filter copsf_abspath to be loaded
      roles: ["corpusops.roles/ansible_plugins"]
      tasks:
      # the variable cops_deploy_ssh_key_paths should have been set at this
      # stage in inventory or via a fact
      - include_role: {name: "corpusops.roles/project/_deploy_key_setup"}
    ```

- Verify after executing your playbook that you have the new files inside the target repository (example here: ``./local/.ssh``)
- Then You can execute the real deployment playbooks that connect underthehood to the removes envs.

