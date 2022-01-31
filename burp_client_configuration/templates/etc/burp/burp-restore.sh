#!/usr/bin/env bash
# {% set data = cops_burpclient_vars %}
# small wrapper to set openssl_cnf
W=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
SSLCONF="$W/openssl.cnf"
BURP_RESTORE_CONFIG="${BURP_RESTORE_CONFIG-$W/burp-client-restore.conf}"
args=""
if [ -e "$BURP_RESTORE_CONFIG" ];then args="-c";fi
if [ -e "$SSLCONF" ];then
    export OPENSSL_CONF="$SSLCONF"
fi
exec burp $args $BURP_RESTORE_CONFIG "$@"
# vim:set et sts=4 ts=4 tw=0:
