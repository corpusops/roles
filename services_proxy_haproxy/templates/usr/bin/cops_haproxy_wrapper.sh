#!/usr/bin/env bash
set -e
if [ "x${DEBUG}" != "x" ];then
    set -x
fi
for i in /etc/default/haproxy /etc/sysconfig/haproxy;do
    if [ -f "$i" ];then
        . "$i"
    fi
done
if [[ -n $CHECK_MODE ]];then
    exec "$HAPROXYB" -c -f "${CONFIG}" ${EXTRAOPTS}
elif [ "x${1}" = "xstart" ];then
    WS=""
    # support for old and new wrapper
    if ( $HAPROXYB --help |grep -- -Ws || /bin/true );then
        WS="-Ws"
    fi
    exec "$HAPROXYB" $WS -f "${CONFIG}" ${EXTRAOPTS} ${PID_ARGS}
fi
exit ${?}
# vim:set et sts=4 ts=4 tw=0 ft=sh:
