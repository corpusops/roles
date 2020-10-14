#!/usr/bin/env bash
cd $(dirname $0)
TEMPO=${TEMPO:-15}
while true;do
     if ! ( ping -c 1 www.google.com );then
         SDEBUG="" DEBUG="1"  sudo -E templates/etc/init.d/qos_voip qos_flush
     fi
     sleep $TEMPO
done
# vim:set et sts=4 ts=4 tw=80:
