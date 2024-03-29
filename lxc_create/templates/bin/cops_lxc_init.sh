#!/usr/bin/env bash
set -x
export DEBIAN_FRONTEND noninteractive
export NONINTERACTIVE=1
if [ ! -d /root/.ssh ];then mkdir -p /root/.ssh;fi
if [ ! -e /root/.ssh/authorized_keys ];then touch /root/.ssh/authorized_keys;fi
retry() {
    tries=$1
    step=$2
    shift;shift
    while true;do
        set +e
        "${@}"
        ret=$?
        set -e
        if [ "x${ret}" = "x0" ];then
            break
        else
            sleep $step
            tries=$(($tries -1))
            if [[ ${tries} -lt 0 ]];then
                break
            fi
        fi
    done
    return $ret
}
rh="/bin/cops_reset-host.py"

marker=/etc/lxc_reset_done
interfaces="
auto lo
iface lo inet loopback
source-directory /etc/network/interfaces.d"
if [ -e /etc/netplan ] && ( which netplan >/dev/null 2>&1 ) && \
  [ -e /tmp/01-netplan-corpusops.yaml ];then
    echo "netplan reconfiguration" >&2
    if [ -e /etc/netplan/10-lxc.yaml ] && \
        ( grep -q eth0 /tmp/01-netplan-corpusops.yaml );then
        rm -f /etc/netplan/10-lxc.yaml
    fi \
    && cp -f /tmp/01-netplan-corpusops.yaml /etc/netplan \
    && netplan generate \
    && netplan apply
    if [ "x${?}" != "x0" ];then
        echo "netplan reconfiguration error" >&2
        exit 1
    fi
elif [ -e /etc/network/interfaces ] && [ -e /tmp/interfaces ];then
    echo "network/interfaces reconfiguration" >&2
    if ( grep -q eth0 /tmp/interfaces );then
        echo "$interfaces" >/etc/network/interfaces
    fi \
    && cp -f /tmp/interfaces /etc/network/interfaces.d/lxc \
    && if [ "x${?}" != "x0" ];then
        echo "network/interfaces reconfiguration error" >&2
        exit 1
    fi
    # can fail on upstart
    ( /etc/init.d/networking restart || /bin/true )
fi

retry 15 1 ping -q -W 4 -c 1 8.8.8.8
if ! which python >/dev/null 2>/dev/null;then
  python=python
  if ( apt-get --version &>/dev/null );then
        if ! ( apt-get install -s $python );then
            apt-get update
            if ! ( apt-get install -s $python );then
                python="python-is-python3"
            fi
        fi
  fi
  retry 15 1 /bin/cops_pkgmgr_install.sh $python \
        || DO_UPDATE=y retry 15 1 /bin/cops_pkgmgr_install.sh $python
  if [ "x${?}" != "x0" ];then
      echo "cant install prerequisites" >&2
      exit 1
  fi
fi

if [ -e "$rh" ] && [ ! -e $marker ];then
    chmod +x "$rh" && \
        "$rh" \
            --origin="{{lxc_container_name}}" \
            --reset-machineid \
            --reset-sshd_keys \
            --reset-ssh \
            --reset-files \
            --reset-postfix
        ret=1
        for i in $(seq 5);do
            if ! ( service ssh restart );then
                sleep 1
            else
                ret=0
                break
            fi
        done
        if [ "x$ret" != "x0" ];then echo "sshrestart failed">&2;exit 1;fi
        touch $marker
fi
# vim:set et sts=4 ts=4 tw=80:
