# registry

- Wrapper to call [vars_registry](../vars_registry) with sensible defaults:

   ``yaml
   cops_vars_registry_global_scope: false
   cops_vars_registry_format_resolve: false
   ```

- Example:

    ```yaml
    - include_role: {name: corpusops.roles/vars_registry}
      {vars: registry_prefix: foo_bar_}
    ```
