#!/usr/bin/env bash
# {{ansible_managed}}
if [ "x${DEBUG}" != "x" ];then set -x;fi
log() { echo "$@" >&2;  }
SKIP_RELOAD=${SKIP_RELOAD-}
reload=${FORCE_HAPROXY_RELOAD-}
# {% set d = corpusops_localsettings_certbot_vars %}
hcertsd="{{d.haproxy_certs_dir}}"
certsd="{{d.configdir}}/live"
domains="{{d.domains|join('\n')}}"
owner="{{d.user}}"
group="{{d.group}}"
howner="{{d.haproxy_owner}}"
hgroup="{{d.haproxy_group}}"
reload_mode="{{d.haproxy_reload_mode}}"
mincertsts=0
if [ ! -e "$hcertsd" ];then
    log "haproxy certs dir $hcertsd doesnt exists"
    exit 0
fi
if [[ -n "$domains" ]];then
while read domain;do
    d="$certsd/$domain"
    t="$hcertsd/$domain.crt"
    ct="$d/haproxy_$domain.crt"
    f="$d/fullchain.pem"
    k="$d/privkey.pem"
    if [ -e "$d" ];then
        if [ -e "$f" ] && [ -e "$k" ];then
            cat "$f" "$k" > "$ct"
            chmod 640 "$ct"
            chown $owner:$group "$ct"
            if [ -e "$t" ] && ( diff -q "$ct" "$t"; ) ;then
                log "lehaproxy: already installed $domain cert ($hcertsd)"
            else
                log "lehaproxy: installing $domain cert ($hcertsd)"
                cp -f "$ct" "$t"
                chmod 640 "$t"
                chown $howner:$hgroup "$t"
                reload=1
            fi
            # Record the certificate which has the latest update date (to restart haproxy in case)
            for ts in $(stat -c "%Y" "$d")  $(stat -c "%Y" "$t");do
                if [[ -n $ts ]] && [ $ts -ge $mincertsts ];then
                    mincertsts=$ts
                fi
            done
        fi
    fi
done <<< "$domains"
fi

is_container() {
    cat -e /proc/1/environ 2>/dev/null|grep -q container=
    echo "${?}"
}

filter_host_pids() {
    pids=""
    if [ "x$(is_container)" != "x0" ];then
        pids="${pids} $(echo "${@}")"
    else
        for pid in ${@};do
            if [ "x$(grep -q /lxc/ /proc/${pid}/cgroup 2>/dev/null;echo "${?}")" != "x0" ];then
                pids="${pids} $(echo "${pid}")"
            fi
         done
    fi
    echo "${pids}" | sed -e "s/\(^ \+\)\|\( \+$\)//g"
}

get_running_haproxy_pid() {
    filter_host_pids $(ps axo pid,cmd|grep "haproxy "|grep -v grep|awk '{print $1}')
}


haproxy_pids=$(get_running_haproxy_pid)
# restart haproxy also if it was started before any new certificate was placed
if [[ -n $haproxy_pids ]];then
    for pid in $haproxy_pids;do
        for lstart in "$(ps axo pid,lstart|grep "$pid "|grep -v grep|head -n1)";do
            dlstart=$(echo "$lstart"|cut -d " " -f2-|sed -e "s/^ //g")
            ts=$(date -d "$dlstart" "+%s")
            if [ $ts -le $mincertsts ];then
                reload=1
            fi
        done
    done
fi
# and we miss his installation through this script
if [[ -z ${SKIP_RELOAD} ]] && [[ -n "${reload}" ]];then
    log "lehaproxy: reload haproxy ($reload_mode)"
    service haproxy $reload_mode
fi
# vim:set et sts=4 ts=4 tw=0:
