#!/usr/bin/env bash
# {{ansible_managed}}
if [ "x${DEBUG}" != "x" ];then set -x;fi
# {% set d = corpusops_localsettings_certbot_vars %}
ret=0
REPO="{{d.repo_dir}}"
W="$(dirname $(readlink -f "$0"))"

fixperms() {
    while read f;do
        chown -Rvf {{d.user}} "$f"
    done < <( cd {{d.home}}  && \
        find *.ini propagate_* le_*.sh *_challenge.sh letsencrypt 2>/dev/null -not -user {{d.user}}  )
}

{% set dnsc='#' %}
{% if d.dns %}
{% set dnsc='' %}
{% endif %}
{{dnsc}}if ! ( su {{d.user}} -c "{{d.home}}/dns_challenge.sh" );then
{{dnsc}}    ret=1
{{dnsc}}fi
{{dnsc}}fixperms

{% set httpc='#' %}
{% if d.http %}
{% set httpc='' %}
{% endif %}
{{httpc}}if ! ( su {{d.user}} -c "{{d.home}}/http_challenge.sh" );then
{{httpc}}    ret=1
{{httpc}}fi
{{httpc}}fixperms

{% set propagatec='#' %}
{% if d.propagate %}
{% set propagatec='' %}
{% endif %}
{{propagatec}}if ! ( su {{d.user}} -c "{{d.home}}/le_propagate.sh" );then
{{propagatec}}    ret=1
{{propagatec}}fi
{{propagatec}}fixperms

{% set pullc='#' %}
{% if d.pull %}
{% set pullc='' %}
{% endif %}
{{pullc}}if ! ( su {{d.user}} -c "{{d.home}}/le_pull.sh" );then
{{pullc}}    ret=1
{{pullc}}fi
{{pullc}}fixperms

{% set haproxyc='#' %}
{% if d.haproxy %}
{% set haproxyc='' %}
{% endif %}
{{haproxyc}}if ! ( {{d.home}}/le_haproxy.sh; );then
{{haproxyc}}    ret=1
{{haproxyc}}fi
{{haproxyc}}fixperms

{{pullc}}if [ -e "$REPO/live" ] && [ -e "$REPO/haproxy" ] && [ -e "$W/le_haproxy.sh" ];then
{{pullc}}    CERTBOT_LIVE_DIR="$REPO/live" \
{{pullc}}        "$W/le_haproxy.sh"
{{pullc}}fi
{{pullc}}fixperms

{% if pullc or httpc or dnsc %}
{% set etcsslc = '' %}
{% else %}
{% set etcsslc = '#' %}
{% endif %}
{{etcsslc}}if ( find "{{d.home}}" -name live -type d | egrep . ) && [ -e "/etc/ssl" ];then
{{etcsslc}}while read f;do rsync -aL "$f/" "/etc/ssl/letsencrypt/";done < <(find "{{d.home}}" -name live -type d)
{{etcsslc}}chown -Rf root:root "/etc/ssl/letsencrypt/"
{{etcsslc}}while read f;do chmod -v 0751 "$f";done < <(find "/etc/ssl/letsencrypt" -type d)
{{etcsslc}}while read f;do chmod -v 0644 "$f";done < <(find "/etc/ssl/letsencrypt" -type f)
{{etcsslc}}fi
{{etcsslc}}fixperms

exit $ret
# vim:set et sts=4 ts=4 tw=0:
