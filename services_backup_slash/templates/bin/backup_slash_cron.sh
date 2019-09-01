#!/usr/bin/env bash
. /etc/profile
ret=0
log() { echo "$@">&2; }
vv() { log "$@";"$@"; }
#
set -ex
{% for i, idata in backup_slash_to_backup_backups.msg.items() %}
i="{{idata.odir}}"
d="{{idata.ddir}}"
if [ ! -e "$d" ];then mkdir -p "$d";fi
if ! ( vv {{vars['corpusops_services_backup_slash_rsync']}} ${i}/ ${d}/ );then
    log "failed to sync $i -> $d"
    ret=1
fi
{% endfor %}
#
exit $ret
# vim:set et sts=4 ts=4 tw=0:
