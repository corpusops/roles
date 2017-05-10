#!/usr/bin/env bash
W=$(cd $(dirname "$0") && pwd)
CW=$(pwd)
COPS_ROOT=/srv/corpusops/corpusops.bootstrap
CONTROLLER_IMAGE="corpusops/ubuntu:14.04"
docker=$(which docker)
runner=${COPSTESTRUNNER:-copsrolestestrunner}
DEBUG=${DEBUG-}
LOGGER_NAME="[unit_role]"
DOCKER_UPGRADE=${DOCKER_UPGRADE-${TRAVIS}}

log() { echo "$LOGGER_NAME ${@}" >&2; }
vv() { log "$LOGGER_NAME ${@}"; "${@}"; }
vvv() { if [[ -n $DEBUG ]];then log "${@}";fi;"${@}"; }
die_in_error_() { if [ "x${1-$?}" != "x0" ];then echo "FAILED: $@">&2; exit 1; fi }
die_in_error() { die_in_error_ $? $@; }
debug() { if [[ -n $DEBUG ]];then log "${@}";fi; }

do_trap_() {
    rc=$?
    func=$1
    sig=$2
    ${func}
    if [ "x${sig}" != "xEXIT" ];then
        kill -${sig} $$
    fi
    exit $rc
}

do_trap() {
    rc=${?}
    func=${1}
    shift
    sigs=${@}
    for sig in ${sigs};do
        trap "do_trap_ ${func} ${sig}" "${sig}"
    done
}

get_id() { docker container inspect -f '{{.Id}}' $@ 2>/dev/null; }
get_runner_id() { get_id $runner; }
get_image_id() { docker image inspect -f '{{.Id}}' $@ 2>/dev/null; }
get_user_img() {
    img="$1"
    if echo $img | grep -vq /;then img="corpusops/$img";fi
    echo $img
}

is_role() {
    local subrole="${1:-$(pwd)}" is_role=1
    for i in test.yml role.yml;do
        if [ -e "$subrole/$i" ];then
            is_role=0
            break
        fi
    done
    return $is_role
}

ALL_ROLES=""
while read subrole;do
    if is_role $subrole;then
        ALL_ROLES="$ALL_ROLES $subrole"
    fi
done < <(find "$W" -mindepth 1 -maxdepth 1 -type d)
# vim:set et sts=4 ts=4 tw=80:
