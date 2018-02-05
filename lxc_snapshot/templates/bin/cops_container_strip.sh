#!/usr/bin/env bash
GIT_SHALLOW_DEPTH=${GIT_SHALLOW_DEPTH}
GIT_SHALLOW=${GIT_SHALLOW-}
NO_IMAGE_STRIP=${NO_IMAGE_STRIP-y}
NO_ANSIBLE_STRIP=${NO_ANSIBLE_STRIP-}
NO_GCC_STRIP=${NO_GCC_STRIP-}
NO_GIT_PACK=${NO_GIT_PACK-}
NO_CLEANUP=${NO_CLEANUP-}
NO_SNAPSHOT=${NO_SNAPSHOT-}
DEB_REMOVES=${DEB_REMOVES-}
COPS_ROOT=${COPS_ROOT:-/srv/corpusops/corpusops.bootstrap}

vv() { echo "$@" >&2;"$@"; }
log() { echo "${@}" >&2; }
debug() { if [[ -n "${DEBUG}" ]];then log "${@}";fi; }
detect_os() {
    # this function should be copiable in other scripts, dont use adjacent functions
    UNAME="${UNAME:-"$(uname | awk '{print tolower($1)}')"}"
    PATH="${PATH}:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games"
    SED="sed"
    if [ "x${UNAME}" != "xlinux" ] && hash -r gsed >/dev/null 2>&1; then
        SED=gsed
    fi
    DISTRIB_CODENAME=""
    DISTRIB_ID=""
    DISTRIB_RELEASE=""
    if hash -r lsb_release >/dev/null 2>&1; then
        DISTRIB_ID=$(lsb_release -si)
        DISTRIB_CODENAME=$(lsb_release -sc)
        DISTRIB_RELEASE=$(lsb_release -sr)
    elif [ -e /etc/lsb-release ];then
        debug "No lsb_release, sourcing manually /etc/lsb-release"
        DISTRIB_ID=$(. /etc/lsb-release;echo ${DISTRIB_ID})
        DISTRIB_CODENAME=$(. /etc/lsb-release;echo ${DISTRIB_CODENAME})
        DISTRIB_RELEASE=$(. /etc/lsb-release;echo ${DISTRIB_RELEASE})
    elif [ -e /etc/os-release ];then
        DISTRIB_ID=$(. /etc/os-release;echo $ID)
        DISTRIB_CODENAME=$(. /etc/os-release;echo $VERSION)
        DISTRIB_CODENAME=$(echo $DISTRIB_CODENAME |sed -e "s/.*(\([^)]\+\))/\1/")
        DISTRIB_RELEASE=$(. /etc/os-release;echo $VERSION_ID)
    elif [ -e /etc/redhat-release ];then
        RHRELEASE=$(cat /etc/redhat-release)
        DISTRIB_CODENAME=${RHRELEASE}
        DISTRIB_RELEASE=${RHRELEASE}
        DISTRIB_ID=${RHRELEASE}
        DISTRIB_CODENAME=$(echo $DISTRIB_CODENAME |sed -e "s/.*(\([^)]\+\))/\1/")
        DISTRIB_RELEASE=$(echo $DISTRIB_RELEASE |sed -e "s/release \([0-9]\)/\1/")
        DISTRIB_ID=$(echo $DISTRIB_ID | awk '{print tolower($1)}')
    else
        if ! ( echo ${@-} | grep -q no_fail );then
            log "unexpected case, no lsb_release"
            exit 1
        fi
    fi
    export DISTRIB_ID DISTRIB_CODENAME DISTRIB_RELEASE
}
detect_os
if [[ -z $NO_GIT_PACK ]] && [[ -e $COPS_ROOT/bin/git_pack ]];then
    vv $COPS_ROOT/bin/git_pack /
fi
if [[ -z $NO_CLEANUP ]] && [[ -e /sbin/cops_container_cleanup.sh ]];then
    vv /sbin/cops_container_cleanup.sh
fi
if [[ -z $NO_SNAPSHOT ]] && [[ -e /sbin/cops_container_snapshot.sh ]];then
    vv /sbin/cops_container_snapshot.sh
fi
if [[ -z $NO_IMAGE_STRIP ]];then
    if [[ -z $NO_ANSIBLE_STRIP ]];then
        for i in $COPS_ROOT/venv/src/ansible/test \
                 $COPS_ROOT/venv/src/ansible/doc*;do
          if [ -e "$i" ];then vv rm -rf "$i";fi
        done
    fi
    if [[ -n "${DEB_REMOVES}" ]];then
        if echo $DISTRIB_ID|egrep -iq "ubuntu|debian|mint";then
            apt-get autoremove -y $DEB_REMOVES
        fi
    fi
fi
# vim:set et sts=4 ts=4 tw=80:
