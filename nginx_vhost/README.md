# corpusops.roles/nginx_vhost ansible role

## Documentation

Managment of nginx vhosts.

### Install a vhost
- Vhosts are composed of three parts by default:
    - A ``site.conf`` file which is installed inside nginxconf/conf.d and generates the server context
    - it includes a ``top.conf``" file which is inside the main context
    - it also includes a ``content.conf`` file which is included inside the server context
- The 3 defaults templates:
    - [site](./templates/site.conf)
    - [top](./templates/top.conf)
    - [content](./templates/content.conf)
- You mostly generally only have have to define the ``content``, maybe the ``top`` (to define maps or upstreams) template for any vhost.
- Exemple
    - templates/top.conf
        ```
        upstream foobar { server foobar:1234;}
        ```

    - templates/content.conf
        ```
        root /foo/bar;
        include proxy_params;
        proxy_pass http://foobar
        ```

    - tasks/main.yml
        ```yaml
        - include_role:
            name: corpusops.roles/nginx_vhost
          vars:
            corpusops_nginx_vhost_basename: foo
            corpusops_nginx_vhost_domain: foo.com
            corpusops_nginx_vhost_server_aliases: [foo.bar]
            corpusops_nginx_vhost_top_template: "../templates/top.conf"
            corpusops_nginx_vhost_content_template: "../templates/content.conf"
        ```

### Remove a vhost
```yaml
- hosts: all
  roles:
    - {role: corpusops.roles/nginx_vhost}
  vars:
    corpusops_nginx_vhost_install: false
    corpusops_nginx_vhost_basename: myvhost
```


## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/nginx_vhost/role.yml \
    --tags=vars,corpusops_vars,corpusops_nginx_vhost_vars
```
