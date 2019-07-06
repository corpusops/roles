#!/usr/bin/env bash
# {{ansible_managed}}
if [ "x${DEBUG}" != "x" ];then set -x;fi
# {% set d = corpusops_localsettings_certbot_vars %}
ret=0
REPO="{{d.repo_dir}}"
W="$(dirname $(readlink -f "$0"))"
{% set dnsc='#' %}
{% if d.dns %}
{% set dnsc='' %}
{% endif %}
{{dnsc}}if ! ( su {{d.user}} -c "{{d.home}}/dns_challenge.sh" );then
{{dnsc}}    ret=1
{{dnsc}}fi

{% set httpc='#' %}
{% if d.http %}
{% set httpc='' %}
{% endif %}
{{httpc}}if ! ( su {{d.user}} -c "{{d.home}}/http_challenge.sh" );then
{{httpc}}    ret=1
{{httpc}}fi

{% set propagatec='#' %}
{% if d.propagate %}
{% set propagatec='' %}
{% endif %}
{{propagatec}}if ! ( su {{d.user}} -c "{{d.home}}/le_propagate.sh" );then
{{propagatec}}    ret=1
{{propagatec}}fi

{% set pullc='#' %}
{% if d.pull %}
{% set pullc='' %}
{% endif %}
{{pullc}}if ! ( su {{d.user}} -c "{{d.home}}/le_pull.sh" );then
{{pullc}}    ret=1
{{pullc}}fi

{% set haproxyc='#' %}
{% if d.haproxy %}
{% set haproxyc='' %}
{% endif %}
{{haproxyc}}if ! ( {{d.home}}/le_haproxy.sh; );then
{{haproxyc}}    ret=1
{{haproxyc}}fi

{{pullc}}if [ -e "$REPO/live" ] && [ -e "$REPO/haproxy" ] && [ -e "$W/le_haproxy.sh" ];then
{{pullc}}    CERTBOT_LIVE_DIR="$REPO/live" \
{{pullc}}        "$W/le_haproxy.sh"
{{pullc}}fi

exit $ret
# vim:set et sts=4 ts=4 tw=0:
