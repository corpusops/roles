#!/usr/bin/env bash
cd "$(dirname ${0})"
W=$(cd .. && pwd)
LOGGER_NAME=pkgmgr

sc=cops_shell_common
[[ ! -e $sc ]] && echo "missing $sc" >&2
. $sc || exit 1

detect_os

usage() {
    echo '
Universal shell wrapper to manage OS package manager
OS SUPPORT: debian(& ubuntu) / archlinux / red-hat (centos/rh/fedora)

[WANTED_EXTRA_PACKAGES="vim"] \
[WANTED_EXTRA_PACKAGES="nano"] \
[DO_SETUP=y] [SKIP_SETUP=y] \
[DO_UPGRADE=y] [SKIP_UPGRADE=y] \
[DO_UPGRADE=y] [SKIP_UPGRADE=y] \
[DO_INSTALL=y] [SKIP_INSTALL=y] \
[DEBUG=y"] \
    '"${0}"' [--help] [packagea] [packageb]'
}

APT_CONF_FILE="/etc/apt/apt.conf.d/01buildconfig"
REQS_PATH="/srv/corpusops.bootstrap/requirements"
NONINTERACTIVE=${NONINTERACTIVE-}
SKIP_SETUP=${SKIP_SETUP-}
SKIP_INSTALL=${SKIP_INSTALL-}
SKIP_UPDATE=${SKIP_UPDATE-}
SKIP_UPGRADE=${SKIP_UPGRADE-}
DO_UPGRADE=${DO_UPGRADE-}
DO_UPDATE=${DO_UPDATE-default}
DO_SETUP=${DO_SETUP-default}
DO_INSTALL=${DO_INSTALL-default}
container=${container-}

###
i_y() {
    if [[ -n ${NONINTERACTIVE} ]]; then
        echo "-y"
    fi
}

###
is_pacman_available() {
    return 1
}

is_pacman_installed() {
    return 1
}

pacman_update() {
    return 1
}

pacman_upgrade() {
    return 1
}

pacman_install() {
    return 1
    vvv pacman install $@
}

ensure_command() {
    local cmd=${1}
    shift
    local pkgs=${@}
    if ! has_command ${cmd}; then
        ${INSTALLER}_install ${pkgs}
    fi
}

pacman_setup() {
    :
}

###
dnf_repoquery() {
    vvv dnf repoquery -q "${@}"
}

is_dnf_available() {
    if ! ( dnf list available ${@} \
           || rh_is_available_but_maybe_provided_by_other ${@}; ) \
           >/dev/null 2>&1; then
        return 1
    fi
}

is_dnf_installed() {
    if ! ( dnf list installed ${@} \
           || rh_is_installed_but_maybe_provided_by_other ${@}; ) \
           >/dev/null 2>&1; then
        return 1
    fi
}

dnf_update() {
    vvv dnf check-update $(i_y)
    ret=$?
    if echo ${ret} | egrep -q '^(0|100)$'; then
        return 0
    fi
    return 1
}

dnf_upgrade() {
    vvv dnf upgrade $(i_y)
}

dnf_install() {
    vvv dnf install $(i_y) $@
}

dnf_ensure_repoquery() {
    if ! ( dnf --help 2>&1 | grep -q repoquery ); then
        dnf_install 'dnf-command(repoquery)'
    fi
}

dnf_setup() {
    rh_setup
}

###
yum_repoquery() {
    repoquery -q "${@}"
}

is_yum_available() {
    if ! ( yum list all ${@} \
           || rh_is_available_but_maybe_provided_by_other ${@}; ) \
        >/dev/null 2>&1; then
        return 1
    else
        return 0
    fi
}

is_yum_installed() {
    if ! ( yum list installed ${@} \
           || rh_is_installed_but_maybe_provided_by_other ${@}; ) \
           >/dev/null 2>&1; then
        return 1
    fi
}

yum_update() {
    vvv yum check-update $(i_y)
    ret=$?
    if echo ${ret} | egrep -q '^(0|100)$'; then
        return 0
    fi
    return 1
}

yum_upgrade() {
    vvv yum upgrade $(i_y)
}

yum_install() {
    yum install $(i_y) $@
}

yum_ensure_repoquery() {
    if ! has_command repoquery; then
        ${INSTALLER}_install yum-utils
    fi
}

yum_setup() {
    rh_setup
}

###
rh_is_available_but_maybe_provided_by_others() {
    ${INSTALLER}_repoquery -q --all       --whatprovides ${@}
}

rh_is_available_but_maybe_provided_by_other() {
    if [[ -z "$(rh_is_available_but_maybe_provided_by_others $@)" ]];then
        return 1
    fi
    return 0
}

rh_is_installed_but_maybe_provided_by_others() {
    ${INSTALLER}_repoquery -q --installed --whatprovides ${@}
}

rh_is_installed_but_maybe_provided_by_other() {
    if [[ -z "$(rh_is_installed_but_maybe_provided_by_others $@)" ]];then
        return 1
    fi
    return 0
}

###
is_aptget_available() {
    if ! apt-cache show ${@} >/dev/null 2>&1; then
        return 1
    else
        return 0
    fi
}

is_aptget_installed() {
    if ! dpkg-query -s ${@} 2>/dev/null|egrep "^Status:"|grep -q installed; then
        return 1
    fi
}

aptget_add_conf() {
    if [[ -n "$2" ]] && grep -q "$2" $APT_CONF_FILE 2>/dev/null;then
        log "test $2 success, skip adding slug $1"
    else
        echo "${1}" >> $APT_CONF_FILE
    fi
}

aptget_update() {
    vvv apt-get update
}

aptget_upgrade() {
    vvv apt-get dist-upgrade
}

aptget_install() {
    vvv apt-get install ${@}
}

aptget_setup() {
    if [[ -n "${NONINTERACTIVE}" ]];then
        export DEBIAN_FRONTEND=noninteractive
        aptget_add_conf "APT::Install-Recommends "0";" "APT::Install-Recommends"
        aptget_add_conf "APT::Get::Assume-Yes "true";" "APT::Get::Assume-Yes"
        aptget_add_conf "APT::Get::force-yes "true";"  "APT::Get::force-yes"
        aptget_add_conf "APT::Install-Suggests "0";"   "APT::Install-Suggests"
    fi
}

rh_setup() {
    ${INSTALLER}_ensure_repoquery
    ensure_command xargs findutils
    ensure_command awk gawk
    ensure_command sort coreutils
    ensure_command egrep grep
    ensure_command which which
}

###
parse_cli() {
    parse_cli_common "${@}"
    if [ "x${DEBIAN_FRONTEND-}" = "noninteractive" ] \
        || [ "x${container-}" = "xdocker" ];then
        NONINTERACTIVE=y
    fi
    WANTED_EXTRA_PACKAGES=${WANTED_EXTRA_PACKAGES-}
    WANTED_PACKAGES=${WANTED_PACKAGES-}
    for i in ${@-};do
        case $i in
            --help|-h) :;;
            *) WANTED_PACKAGES="${WANTED_PACKAGES} ${i}";;
        esac
    done
    WANTED_PACKAGES="$(echo "$(echo "${WANTED_PACKAGES}" | xargs -n1 | sort -u)")"
    WANTED_EXTRA_PACKAGES="$(echo "$(echo "${WANTED_EXTRA_PACKAGES}" | xargs -n1 | sort -u)")"
    if echo ${DISTRIB_ID} | egrep -iq "ubuntu|debian";then
        INSTALLER=aptget
    elif echo ${DISTRIB_ID} | egrep -iq "archlinux";then
        INSTALLER=pacman
    elif echo ${DISTRIB_ID} | egrep -iq "redhat|red-hat|centos|fedora";then
        INSTALLER=yum
        if has_command dnf;then
            INSTALLER=dnf
        fi
    else
        die "Not supported os"
    fi
    debug "INSTALLER: ${INSTALLER}"
}

update() {
    if [[ -z "${SKIP_UPDATE}" ]] && [[ -n "${DO_UPDATE}" ]];then
        log ${INSTALLER}_update
        ${INSTALLER}_update
        may_die $? $? "Update failed"
    else
        debug "Skip update"
    fi
}

prepare_install() {
    candidates=""
    already_installed=""
    secondround=""
    secondround_extra=""
    if [[ -z "${SKIP_INSTALL}" ]];then
        # test if all packages are there
        if [[ -n "${WANTED_PACKAGES}" ]]; then
            for i in $WANTED_PACKAGES;do
                if ! is_${INSTALLER}_installed $i;then
                    if is_${INSTALLER}_available ${i}; then
                        candidates="${candidates} ${i}"
                    else
                        secondround="${secondround} ${i}"
                        warn "Package '${i}' not found before update"
                    fi
                else
                    debug "Package '${i}' found"
                    already_installed="${already_installed} ${i}"
                fi
            done
        fi
        if [[ -n "${WANTED_EXTRA_PACKAGES}" ]]; then
            for i in $WANTED_EXTRA_PACKAGES;do
                if ! is_${INSTALLER}_installed ${i}; then
                    if is_${INSTALLER}_available ${i};then
                        candidates="${candidates} ${i}"
                    else
                        secondround_extra="${secondround_extra} ${i}"
                        warn "EXTRA Package '${i}' not found before update"
                    fi
                else
                    debug "EPackage '${i}' found"
                    already_installed="${already_installed} ${i}"
                fi
            done
        fi
        # skip update & rest if everything is there
        if [[ -z "${candidates}" ]];then
            if [ "x${DO_UPDATE}" = "xdefault" ];then
                DO_UPDATE=""
            fi
        fi
        #
        #
        update
        #
        #
        # after update, check for packages that werent found at first
        # if we can now resolve them
        if [[ -n "${secondround}" ]]; then
            for i in ${secondround};do
                if ! is_${INSTALLER}_installed $i;then
                    if is_${INSTALLER}_available ${i}; then
                        candidates="${candidates} ${i}"
                    else
                        die "Package '${i}' not found"
                    fi
                else
                    debug "PostPackage '${i}' found"
                    already_installed="${already_installed} ${i}"
                fi
            done
        fi
        if [[ -n "${secondround_extra}" ]]; then
            for i in ${secondround_extra};do
                if ! is_${INSTALLER}_installed ${i}; then
                    if is_${INSTALLER}_available ${i};then
                        candidates="${candidates} ${i}"
                    else
                        warn "EXTRA Package '${i}' not found"
                    fi
                else
                    debug "PostEPackage '${i}' found'"
                    already_installed="${already_installed} ${i}"
                fi
            done
        fi

    else
        debug "Skip pre-flight install"
    fi
    candidates=$( echo "${candidates}" | xargs -n1 | sort -u )
    already_installed=$( echo "${already_installed}" | xargs -n1 | sort -u )
    if [[ -n "${candidates}" ]]; then
        log "Will install: $(echo ${candidates})"
    fi
    if [[ -n "${already_installed}" ]]; then
        log "Already installed: $(echo ${already_installed})"
    fi
}

setup() {
    if [[ -z "${SKIP_SETUP}" ]] &&  [[ -n "${DO_SETUP}" ]];then
        debug ${INSTALLER}_setup
        ${INSTALLER}_setup
        may_die $? $? "setup failed"
    else
        debug "Skip setup"
    fi
}

upgrade() {
    if [[ -z "${SKIP_UPGRADE}" ]] &&  [[ -n "${DO_UPGRADE}" ]];then
        log ${INSTALLER}_upgrade
        ${INSTALLER}_upgrade
        may_die $? $? "upgrade failed"
    else
        debug "Skip upgrade"
    fi
}

install() {
    upgrade
    if [[ -z "${SKIP_INSTALL}" ]] \
        && [[ -n "${DO_INSTALL}" ]] \
        && [[ -n "${candidates}" ]]; then
        log ${INSTALLER}_install ${candidates}
        ${INSTALLER}_install ${candidates}
        may_die $? $? "install failed"
    else
        debug "Skip install"
    fi
}

parse_cli "${@}"
setup
prepare_install  # calls: update
upgrade
install
# vim:set et sts=4 ts=4 tw=80:
