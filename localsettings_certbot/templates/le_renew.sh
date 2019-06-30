#!/usr/bin/env bash
# {{ansible_managed}}
if [ "x${DEBUG}" != "x" ];then set -x;fi
# {% set d = corpusops_localsettings_certbot_vars %}
ret=0
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
{% set haproxyc='#' %}
{% if d.haproxy %}
{% set haproxyc='' %}
{% endif %}
{{haproxyc}}if ! ( {{d.home}}/le_haproxy.sh; );then
{{haproxyc}}    ret=1
{{haproxyc}}fi
exit $ret
# vim:set et sts=4 ts=4 tw=0:
