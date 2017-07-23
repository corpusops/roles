# corpusops.roles/docker_compose_service ansible role

## Documentation

- Install a docker compose file as a system service (systemd, or upstart)

### Install a dockercompose file as a system service
```yaml
- include_role:
    name: corpusops.roles/docker_compose_service
  vars:
    _docker_compose_service:
     project: "compse-myapp"
     working_directory: "/home/myapp"
```

- See [defaults](./defaults/main.yml) for additionnal options variables<br/>
  Maybe not up to date:

    ```yaml
    _docker_compose_service:
      project: compose-myapp
      working_directory: /tmp
      docker_compose_file: docker-compose.yml
      service_activated: true
    ```
