#!/usr/bin/env bash
set -ex
cd $(dirname $0)
container=$(echo $(basename $(dirname $(readlink -f $0))))
lxcap=$(echo $(dirname $(readlink -f $0)))
lxcp=$(echo $(dirname $(dirname $(readlink -f $0))))
for i in bin/cops_container_snapshot.sh;do
    if [ -e $i ];then
        cat $i | lxc-attach -P "$lxcp" -n $container -- tee /$i
        lxc-attach -P "$lxcp" -n $container -- chmod +x /$i
    fi
done
lxc-attach -P "${lxcp}" -n $container -- bash bin/cops_container_snapshot.sh
# vim:set et sts=4 ts=4 tw=80:
