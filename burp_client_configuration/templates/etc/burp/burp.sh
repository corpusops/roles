#!/usr/bin/env bash
set -e
W=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
SSLCONF="$W/openssl.cnf"
args=""
BURP_CONFIG="${BURP_CONFIG-$W/burp-client.conf}"
if [[ -n ${DEBUG-} ]];then set -x;fi
if [ -e $BURP_CONFIG ];then args="-c";fi
if [ -e "$SSLCONF" ];then
    export OPENSSL_CONF="$SSLCONF"
fi
exec burp $args $BURP_CONFIG "$@"
# vim:set et sts=4 ts=4 tw=0:
