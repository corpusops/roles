#!/usr/bin/env bash
# {{ansible_managed}}
if [ "x${DEBUG}" != "x" ];then set -x;fi
log() { echo "$@" >&2;  }
# {% set d = corpusops_localsettings_certbot_vars %}
CERTBOT_LIVE_DIR="${CERTBOT_LIVE_DIR:-{{d.configdir}}/live}"
owner="${CERTBOT_OWNER:-{{d.user}}}"
group="${CERTBOT_GROUP:-{{d.group}}}"
if [ -e "$CERTBOT_LIVE_DIR" ];then
while read d;do
    domain=$(basename $d)
    ct="$d/haproxy_$domain.crt"
    nct="$d/nginx_$domain.crt"
    f="$d/fullchain.pem"
    k="$d/privkey.pem"
    if [ -e "$d" ];then
        if [ -e "$f" ] && [ -e "$k" ];then
            cat "$f" "$k" > "$ct"
            cat "$k" "$f" > "$nct"
            chmod 640 "$ct"
            chown $owner:$group "$ct"
        fi
    fi
done < <(find "$CERTBOT_LIVE_DIR" -mindepth 1 -maxdepth 1 -type d)
fi
# vim:set et sts=4 ts=4 tw=0:
