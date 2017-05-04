#!/usr/bin/env bash
vv() { echo "$@" >&2;"$@"; }
COPS_ROOT=${COPS_ROOT:-/src/corpusops/corpusops.bootstrap}
if [[ -z $NO_GIT_PACK ]] && [[ -e $COPS_ROOT/bin/git_pack ]];then
    vv $COPS_ROOT/bin/git_pack /
fi
if [[ -z $NO_CLEANUP ]] && [[ -e /sbin/cops_container_cleanup.sh ]];then
    vv /sbin/cops_container_cleanup.sh
fi
if [[ -z $NO_SNAPSHOT ]] && [[ -e /sbin/cops_container_snapshot.sh ]];then
    vv /sbin/cops_container_snapshot.sh
fi
# vim:set et sts=4 ts=4 tw=80:
