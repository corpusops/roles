#!/usr/bin/env bash
# {% set data = corpusops_services_mail_postfix_vars %}
# {% set sd = corpusops_services_mail_postfix_vars.spool %}
set -e
for i in\
    "{{sd}}/active"   \
    "{{sd}}/bounce"   \
    "{{sd}}/corrupt"  \
    "{{sd}}/defer"    \
    "{{sd}}/deferred" \
    "{{sd}}/flush"    \
    "{{sd}}/hold"     \
    "{{sd}}/incoming" \
    "{{sd}}/private"  \
    "{{sd}}/saved"    \
    "{{sd}}/trace"    \
    ;do if [ -e "${i}" ];then chown postfix:root "${i}";fi;done
for i in\
  "{{data.prefix}}/certificate.key"              \
  "{{data.prefix}}/certificate.pub"              \
  "{{data.prefix}}/dynamicmaps.cf"               \
  "{{data.prefix}}/postfix-script"               \
  "{{data.prefix}}/post-install"                 \
  {% for i in data.hashtables -%}
  "{{data.prefix}}/{{i}}"                 \
  "{{data.prefix}}/{{i}}.db"              \
  "{{data.prefix}}/{{i}}.local"           \
  "{{data.prefix}}/{{i}}.local.db"        \
  {% endfor %} ;do
if [ -e "${i}" ];then chown root:postfix "${i}";fi;done
for i in /usr/sbin/postdrop  /usr/sbin/postqueue ;do
if [ -e "${i}" ];then
    chmod g-s "${i}"; chown root:postdrop "${i}";chmod g+s "${i}";fi;done
if [ -e "{{sd}}/public" ];then
    chmod g-s              "{{sd}}/public"
    chown postfix:postdrop "{{sd}}/public"
    chmod g+s              "{{sd}}/public"
fi
if [ -e "{{sd}}/maildrop" ];then chown postfix:postdrop "{{sd}}/maildrop";fi
if [ -e /var/lib/postfix ];then chown -Rf postfix:postdrop /var/lib/postfix;fi
# vim:set et sts=4 ts=4 tw=0:
