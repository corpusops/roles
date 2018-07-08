# corpusops.roles/docker_compose_service ansible role

## Documentation

- Install a docker compose file as a system service (systemd, or upstart)

### Install a dockercompose file as a system service
```yaml
- include_role:
    name: corpusops.roles/docker_compose_service
  vars:
    _docker_compose_service:
      path: "/home/myapp"
      files: [docker-compose.yml, docker-compose-prod.yml]
```

- On ``start``, this check compose config, then pull image, then start.
- On ``down``, this stop services, and run down afterwards.

- See [defaults](./defaults/main.yml) for additionnal options variables<br/>
  Maybe not up to date:

    ```yaml
    _docker_compose_service:
      # working directory for compose file
      path: /tmp
      # files to use for docker-compose calls
      files: [docker-compose.yml]
      # name of the systemd service to install, default to directory basename
      project: null
      service_activated: true/false
      args: common args for all cmds
      state: service state configured
      pull_args: args at docker-compose pull time, default to args
      config_args: args at docker-compose config time, default to args
      up_args: args at docker-compose up time, default to args
      stop_args: args at docker-compose stop time, default to args
      down_args: args at docker-compose down time, default to args
      requires: systemd Unit requires slot
      before: systemd Unit before slot
      after: systemd Unit after slot
      wantedby: systemd Unit wantedby slot
      restart: systemd Unit restart slot ("no")
      restart_sec: systemd Unit restart_sec slot ("0")
      timeout_sec: (systemd Unit timeout_sec slot "300")
    ```
