#!/usr/bin/env bash
# {{ansible_managed}}

get_command() {
    local p=
    local cmd="${@}"
    if which which >/dev/null 2>/dev/null;then
        p=$(which "${cmd}" 2>/dev/null)
    fi
    if [ "x${p}" = "x" ];then
        p=$(export IFS=:;
            echo "${PATH-}" | while read -ra pathea;do
                for pathe in "${pathea[@]}";do
                    pc="${pathe}/${cmd}";
                    if [ -x "${pc}" ]; then
                        p="${pc}"
                    fi
                done
                if [ "x${p}" != "x" ]; then echo "${p}";break;fi
            done )
    fi
    if [ "x${p}" != "x" ];then
        echo "${p}"
    fi
}
has_command() {
    ret=1
    if which which >/dev/null 2>/dev/null;then
      if which "${@}" >/dev/null 2>/dev/null;then
        ret=0
      fi
    else
      if command -v "${@}" >/dev/null 2>/dev/null;then
        ret=0
      else
        if hash -r "${@}" >/dev/null 2>/dev/null;then
            ret=0
        fi
      fi
    fi
    return ${ret}
}

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



if [ "x${DEBUG}" != "x" ];then set -x;fi
log() { echo "$@" >&2;  }
SKIP_RELOAD=${SKIP_RELOAD-}
SKIP_INSTALL=${SKIP_INSTALL-}
if ! ( has_command haproxy );then
    FORCE_HAPROXY_RELOAD=
fi
reload=${FORCE_HAPROXY_RELOAD-}
# {% set d = corpusops_localsettings_certbot_vars %}
HAPROXY_CERTS_DIR="${HAPROXY_CERTS_DIR:-{{d.haproxy_certs_dir}}}"
CERTBOT_LIVE_DIR="${CERTBOT_LIVE_DIR:-{{d.configdir}}/live}"
owner="{{d.user}}"
group="{{d.group}}"
howner="{{d.haproxy_owner}}"
hgroup="{{d.haproxy_group}}"
reload_mode="{{d.haproxy_reload_mode}}"
mincertsts=0
if [ ! -e "$HAPROXY_CERTS_DIR" ];then
    log "haproxy certs dir $HAPROXY_CERTS_DIR doesnt exists, creating it"
    mkdir -p "$HAPROXY_CERTS_DIR"
    chown "$owner:$group" "$HAPROXY_CERTS_DIR"
    chmod o-rwx "$HAPROXY_CERTS_DIR"
fi
if [ -e "$CERTBOT_LIVE_DIR" ];then
while read d;do
    domain=$(basename $d)
    t="$HAPROXY_CERTS_DIR/$domain.crt"
    ct="$d/haproxy_$domain.crt"
    f="$d/fullchain.pem"
    k="$d/privkey.pem"
    if [ -e "$d" ];then
        if [ -e "$f" ] && [ -e "$k" ];then
            cat "$f" "$k" > "$ct"
            chmod 640 "$ct"
            chown $owner:$group "$ct"
            if [[ -z ${SKIP_INSTALL} ]];then
                if [ -e "$t" ] && ( diff -q "$ct" "$t"; ) ;then
                    log "lehaproxy: already installed $domain cert ($HAPROXY_CERTS_DIR)"
                else
                    log "lehaproxy: installing $domain cert ($HAPROXY_CERTS_DIR)"
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
    fi
done < <(find "$CERTBOT_LIVE_DIR" -mindepth 1 -maxdepth 1 -type d)
fi

if [[ -z ${SKIP_RELOAD} ]];then
    haproxy_pids=$(get_running_haproxy_pid)
    # restart haproxy also if it was started before any new certificate was placed
    if ( has_command haproxy ) && [[ -n $haproxy_pids ]];then
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
    if [[ -n "${reload}" ]];then
        log "lehaproxy: reload haproxy ($reload_mode)"
        service haproxy $reload_mode
    fi
fi
# vim:set et sts=4 ts=4 tw=0:
