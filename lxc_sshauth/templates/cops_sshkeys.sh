#!/usr/bin/env bash
container=$(echo $(basename $(dirname $(readlink -f $0))))
lxcap=$(echo $(dirname $(readlink -f $0)))
lxcp=$(echo $(dirname $(dirname $(readlink -f $0))))
keysf="$lxcap/sshkeys.pub"
if [ ! -e  ];then
    echo "No keys to add"
    exit 1
fi
cd "$lxcap/sshkeys"
if ! ( lxc-attach -e -P "${lxcp}" -n $container -- test  -e /root/.ssh );then
    echo "-CHANGED- Creating lxc root ssh folder"
    lxc-attach -P "${lxcp}" -n $container -- mkdir /root/.ssh
fi
if ! ( lxc-attach -e -P "${lxcp}" -n $container -- test -e /root/.ssh/authorized_keys );then
    echo "-CHANGED- Creating lxc root ssh authorized_keys"
    lxc-attach -e -P "${lxcp}" -n $container -- touch /root/.ssh/authorized_keys
fi
lxc-attach -P "${lxcp}" -n $container -- /bin/sh -c "chmod 700 /root/.ssh;chmod 600 /root/.ssh/authorized_keys"
while read f;do
    while read sshkey;do
        if echo "$sshkey" | grep -E "^\s*$";then
            echo empty line >&2
        elif ! ( ( lxc-attach -e -P "${lxcp}" -n $container -- \
                   cat /root/.ssh/authorized_keys ) |\
             grep -q -- "$sshkey" );
        then
            echo "-CHANGED-Add $sshkey"
            ( printf "\n${sshkey}\n" | \
                lxc-attach -P "${lxcp}" -n $container -- \
                tee -a /root/.ssh/authorized_keys ) >/dev/null 2>&1
        fi
    done < <(cat "$f")
done < <(find -type f)
# vim:set et sts=4 ts=4 tw=80:
