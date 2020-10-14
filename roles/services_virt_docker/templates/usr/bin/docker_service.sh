#!/usr/bin/env bash
for i in \
 /etc/default/docker \
 /etc/default/docker-storage \
 /etc/default/docker-network \
 /etc/sysconfig/docker \
 /etc/sysconfig/docker-storage \
 /etc/sysconfig/docker-network \
 ;do
  if test -e "${i}"; then
    echo loading "$i"
    . "${i}"
  fi
done
exec $DOCKERD $DOCKER_OPTS
# vim:set et sts=4 ts=4 tw=80:
