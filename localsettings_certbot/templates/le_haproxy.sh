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
        fi
    fi
done <<< "$domains"
fi
if [[ -z ${SKIP_RELOAD} ]] && [[ -n "${reload}" ]];then
    service haproxy $reload_mode
fi
# vim:set et sts=4 ts=4 tw=0:
