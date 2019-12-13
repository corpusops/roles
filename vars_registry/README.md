# corpusops.roles/vars_registry ansible role
## Documentation
- Problem is that when you have a ``dict`` variable inside your variables,
  you can't redefine one of the subelements without redefining the whole dict.
- This simple role to define a variable registry
  (a dict that contain nested settings knobs)
  from other well named variables.
- This role lets you do this by redefining at run time an extra variable
  that will contain the original dict augmented by your nested keys.

### Order of precedence
- registry dict (``foo: {A: B}``)
- registry overrides (``foo_overrides: {A: B}``)
- flattened variables (``foo_A: B``)

### Usage
- imagine that you have in ``defaults/main.yml`` or somewhere in your variables:

    ```yaml
    ---
    foo_bar:
      truc: muche
      other: goo
    foo_bar_truc: bar
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
    foo_bar_vars:
      truc: bar
      other: goo
    ```

- One other way is either to redefine a part of the dict by another dict
  where the key is ``_$var`` in ``defaults/main.yml`` or somewhere in your variables:

    ```yaml
    ---
    foo_bar_vars:
      truc: muche
      other: goo
    _foo_bar:
      truc: 2222
    ```

- One other way is either to define the whole default registry dict is
  as usual in ``defaults/main.yml`` or somewhere in your variables:

    ```yaml
    ---
    foo_bar_truc: other1
    ```

- To define defaults values that won't interfer with any of thos ways, and then
  let the user free to use any of the dict form or the flatten form to override particular values in
  the registry, you can use the special ``___<prefix>`` form this way:

    ```yaml
    # this form that wont have any conflict with the overriding forms (flatten or dict) is this one:
    # ___<prefiv>: {var: foo}
    # so
    ___foo_bar:
      truc: other1
    ```
- You noticed that by default:
    - the extra var name is ``${you_var}_vars``
    - the prefix for variables is ``${you_var}_``

- You can override this by setting:

    - ``cops_vars_registry_target``: dict variable inside the inventory to get defaults from
    - ``cops_vars_registry_prefix``: prefix to get variables overrides from
    - ``cops_vars_registry_overrides``: variable to get overrides from
    - ``cops_vars_registry_name``: final variable name

### Updating a complex variable: tips'n'tricks
- To let users redefine/rework later in the deployment process lists or dict, we added the ``<triple_>default``: ``___default`` machinery:
    ```yaml
    ---
    foo_muche___default: [1, 2]
    # =>
    foo_muche___default: [1, 2]
    foo_muche: [1, 2]
    foo_vars:
      muche: [1, 2]
      muche___default: [1, 2]
    ```
- Then later, to update a list, you can use something like the

  ```yaml
  custom_muche: [3, 4]
  foo_muche: "{{foo_muche____default+custom_muche}}"
  ```

- Then later, to update a dict, you can use something like the

  ```yaml
  foo_muche___default: {1: 2}
  custom_muche: {3, 4}
  foo_muche: "{{(
      ( vars['foo_muche___default']|copsf_deepcopy)
      | copsf_dictupdate(custom_muche)
      | to_json
      )}}"
  ```


## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/vars_registry/role.yml \
    --tags=vars,corpusops_vars,corpusops_vars_registry
```
