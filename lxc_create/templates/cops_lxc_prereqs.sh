#!/usr/bin/env bash
set -e
cd $(dirname $0)
container=$(echo $(basename $(dirname $(readlink -f $0))))
lxcap=$(echo $(dirname $(readlink -f $0)))
lxcp=$(echo $(dirname $(dirname $(readlink -f $0))))
for i in \
    tmp/01-netplan-corpusops.yaml \
    bin/cops_shell_common \
    bin/cops_pkgmgr_install.sh \
    bin/cops_reset-host.py \
    bin/cops_lxc_init.sh;do
    if [ -e $i ];then
        echo "copying $i" >&2
        ( cat $i | lxc-attach -P "$lxcp" -n $container -- tee /$i ) >/dev/null
        lxc-attach -P "$lxcp" -n $container -- chmod +x /$i
    fi
done
echo "Running /bin/cops_lxc_init.sh in $container ($lxcp)" >&2
lxc-attach -P "${lxcp}" -n $container -- bash /bin/cops_lxc_init.sh
# vim:set et sts=4 ts=4 tw=80:
