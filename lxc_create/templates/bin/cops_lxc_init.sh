#!/usr/bin/env bash
export DEBIAN_FRONTEND noninteractive
export NONINTERACTIVE=1
if [ ! -d /root/.ssh ];then mkdir -p /root/.ssh;fi
if [ ! -e /root/.ssh/authorized_keys ];then touch /root/.ssh/authorized_keys;fi
retry() {
    tries=$1
    step=$2
    shift;shift
    while true;do
        "${@}"
        ret=$?
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
retry 15 1 ping -q -W 4 -c 1 8.8.8.8
if ! which python >/dev/null 2>/dev/null;then
  retry 15 1 /bin/cops_pkgmgr_install.sh python
  if [ "x${?}" != "x0" ];then
      echo "cant install prerequisites" >&2
      exit 1
  fi
fi
rh="/bin/cops_reset-host.py"
marker=/etc/lxc_reset_done
if [ -e "$rh" ] && [ ! -e $marker ];then
    chmod +x "$rh" && \
        "$rh" \
            --origin="{{lxc_container_name}}" \
            --reset-sshd_keys \
            --reset-ssh \
            --reset-files \
            --reset-postfix &&\
        touch $marker &&\
        service ssh restart
fi
# vim:set et sts=4 ts=4 tw=80:
