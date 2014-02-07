#!/usr/bin/env bash
SOFT_STRIP=y
if echo ${container-}|grep -iq docker;then
    SOFT_STRIP=
fi
GIT_SHALLOW_DEPTH=${GIT_SHALLOW_DEPTH}
GIT_SHALLOW=${GIT_SHALLOW-}
NO_IMAGE_STRIP=${NO_IMAGE_STRIP-$SOFT_STRIP}
NO_YUM_CLEANUP=${NO_YUM_CLEANUP-}
NO_ANSIBLE_STRIP=${NO_ANSIBLE_STRIP-}
NO_GIT_DESTROY=${NO_GIT_DESTROY-1}
NO_ANSIBLE_GIT_DESTROY=${NO_ANSIBLE_GIT_DESTROY-${NO_GIT_DESTROY}}
NO_PYC_STRIP=${NO_PYC_STRIP-}
NO_DOC_STRIP=${NO_DOC_STRIP-$SOFT_STRIP}
NO_GCC_STRIP=${NO_GCC_STRIP-$SOFT_STRIP}
NO_GIT_PACK=${NO_GIT_PACK-}
NO_CLEANUP=${NO_CLEANUP-}
NO_MAN_STRIP=${NO_MAN_STRIP-$SOFT_STRIP}
NO_SNAPSHOT=${NO_SNAPSHOT-}
PKGS_REMOVES=${PKGS_REMOVES-}
DEV_AUTOREMOVE=${DEV_AUTOREMOVE-}
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
strip_git() {
    local corpusopsgit=$1
    if [ -e $corpusopsgit ];then
        cd $corpusopsgit/..
        git log|xz>git_log.gz
        echo "rm -rvf $corpusopsgit"
        rm -rf $corpusopsgit
        cd ..
    fi
}
deb_filter_pkg_in_cache() {
    local pkgs=
    for i in $@;do
        if apt-cache show $i >/dev/null 2>&1;then
            pkgs="$pkgs $i"
        fi
    done
    echo $pkgs
}
rh_filter_pkg_in_cache() {
    local pkgs=
    for i in $@;do
        if yum info $i >/dev/null 2>&1;then
            pkgs="$pkgs $i"
        fi
    done
    echo $pkgs
}
detect_os
MAN_DIRS=${MAN_DIRS:-"
/usr/share/man
/usr/local/share/man
"}
DOC_DIRS=${DOC_DIRS:-"
/usr/share/info
/usr/local/share/info
/usr/share/doc
/usr/local/share/doc
"}
DOC_STRIPS=${DOC_STRIPS:-"
*.info.gz
news*
readme*
author*
license*
copyright*
deb*
ubuntu*
todo*
changelog*
changes*
coding_style*
distro_porting*
differences*
history*
ack*
*notes*
thank*
faq*
bug*
"}
DOC_RM=${DOC_RM:-"
 python git/RelNotes socat/socat.html"}
if [[ -z $NO_DOC_STRIP ]];then
    while read docdir;do
        if [ -d "$docdir" ];then
            for i in $DOC_RM;do
                d="$docdir/$i"
                if [ -e "$d" ];then vv rm -rf $d;fi
            done
            while read sdocdir;do
                for pattern in $DOC_STRIPS;do
                    find $sdocdir -iname "$pattern" -delete -type f
                done
            done < <(find $docdir -maxdepth 1 -mindepth 1)
        fi
    done <<< "$DOC_DIRS"
fi
if [[ -z $NO_MAN_STRIP ]];then
    while read mandir;do
        if [ -d "$mandir" ];then
            log "Wiping manpages in: $mandir"
            while read i;do rm -f "$i"
            done < <(find "$mandir" -type f)
        fi
    done <<< "$MAN_DIRS"
fi
if [[ -z $NO_CLEANUP ]] && [[ -e /sbin/cops_container_cleanup.sh ]];then
    vv /sbin/cops_container_cleanup.sh
fi
if [[ -z ${NO_PYC_STRIP} ]];then
    find / -type f -name "*.pyc" -delete
fi
if [[ -z ${NO_YUM_CLEANUP} ]];then
    if echo $DISTRIB_ID|grep -E -iq "redhat|red-hat|ol|centos";then
        vv rm -rf /usr/lib/firmware/*
        for i in /var/cache/yum;do
            if [ -e "$î" ];then
                vv rm -rf "$i"
            fi
        done
    fi
fi
if [[ -z $NO_SNAPSHOT ]] && [[ -e /sbin/cops_container_snapshot.sh ]];then
    vv /sbin/cops_container_snapshot.sh
fi
if [[ -z $NO_IMAGE_STRIP ]];then
    if [[ -z $NO_ANSIBLE_STRIP ]];then
        for aroot in /usr/src/corpusops/ansible $COPS_ROOT/venv/src/ansible;do
            if [[ -z $NO_ANSIBLE_GIT_DESTROY ]];then
                strip_git $aroot/.git
            fi
            for aps in $aroot/test $aroot/doc*;do
                if [ -e "$aps" ];then
                    vv rm -rf "$aps"
                fi
            done
        done
    fi
    if [[ -z $NO_GIT_DESTROY ]];then
        strip_git $COPS_ROOT/roles/corpusops.roles/.git
        strip_git $COPS_ROOT/.git
    fi
fi
if [[ -z $NO_GIT_PACK ]] && [[ -e $COPS_ROOT/bin/git_pack ]];then
    vv $COPS_ROOT/bin/git_pack /
fi
if [[ -z $NO_IMAGE_STRIP ]];then
    if echo $DISTRIB_ID|grep -E -iq "redhat|red-hat|ol|centos";then
        # remove dev pkgs
        # while manually installing their lib counterpart
        if [[ -n "${DEV_AUTOREMOVE}" ]];then
            devpkgs=$(rpm -qa|grep -E  -- "-devel|-header)")
            pkgs=$(rpm -qa|grep -E  -- "-devel|-header"\
                   |sed -re "s/(-devel|-header).*//g")
            for i in $(rh_filter_pkg_in_cache $pkgs);do
                vv yum install -y $i || /bin/true
            done
            vv yum autoremove -y $(rh_filter_pkg_in_cache $devpkgs)
        fi
        # remove some unwanted pkgs
        if [[ -n "${PKGS_REMOVES}" ]];then
            vv yum autoremove -y  $(rh_filter_pkg_in_cache $PKGS_REMOVES)
        fi
    fi
    if echo $DISTRIB_ID|grep -E -iq "ubuntu|debian|mint";then
        # remove dev pkgs
        # while manually installing their lib counterpart
        if [[ -n "${DEV_AUTOREMOVE}" ]];then
            devpkgs=$(dpkg -l\
                |grep ii|grep -- -dev\
                |awk '{print $2}'\
                |sed -re "s/:(amd64|i386)//g")
            pkgs=""
            for i in $devpkgs;do
                pkgs="$pkgs ${pkg//-dev}"
            done
            for i in $(deb_filter_pkg_in_cache $pkgs);do
                vv apt-get install \
                    --ignore-missing \
                    --no-install-recommends -y \
                    $i || /bin/true
            done
            vv apt-get remove --auto-remove -y \
                $(deb_filter_pkg_in_cache $devpkgs)
        fi
        # remove some unwanted pkgs
        if [[ -n "${PKGS_REMOVES}" ]];then
            vv apt-get autoremove -y \
                $(deb_filter_pkg_in_cache $PKGS_REMOVES)
        fi
    fi
fi
# vim:set et sts=4 ts=4 tw=80:
