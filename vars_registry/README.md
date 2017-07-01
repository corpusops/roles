# corpusops.roles/vars_registry ansible role
## Documentation
- Problem is that when you have a ``dict`` variable inside your variables,
  you can't redefine one of the subelements without redefining the whole dict.
- This simple role to define a variable registry
  (a dict that contain nested settings knobs)
  from other well named variables.
- This role lets you do this by redefining at run time an extra variable
  that will contain the original dict augmented by your nested keys.

### Usage
- imagine that you have:

    ```yaml
    ---
    foo_var:
        truc: muche
        other: goo
    foo_var_truc: bar
    ```

- And in a task you do:

    ```yaml
    ---
    - include_role: {name: corpusops.roles/vars_registry}
      vars:
        cops_vars_registry_target: foo_var
    ```

- For the rest of the play, you ll have a variable named ``foo_bar_vars`` with the value:

    ```yaml
    ---
    foo_var:
        truc: bar
        other: goo

    ```

- You noticed that by default:
    - the extra var name is ``${you_var}_vars``
    - the prefix for variables is ``${you_var}_``

- You can override this by setting:
    - ``cops_vars_registry_target``: dict variable inside the inventory to get defaults from
    - ``cops_vars_registry_prefix``: prefix to get variables overrides from
    - ``cops_vars_registry_name``: final variable name

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/vars_registry/role.yml \
    --tags=vars,corpusops_vars,corpusops_vars_registry
```
