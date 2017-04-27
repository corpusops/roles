#!/usr/bin/env bash
# Either test on docker if possible or directly on travis compute node
. test_env.sh
post_tests_cleanup() {
    if [[ -n "${NO_CLEANUP}" ]]; then
        log "Skip Post tests cleanup"
    else
        for test_docker in ${runner};do
            test_dockerid=$(get_id ${test_docker})
            if [[ -n "${test_dockerid}" ]]; then
                log "Removing produced test docker: ${test_docker}"
                vvv docker rm -f "${test_dockerid}" >/dev/null
            fi
        done
    fi
}

setup() {
    vvv sudo "$docker" run -ti -d --name=$runner \
        $( while read v; do echo " -v ${v}:${v}:ro";done < \
          <( ldd "${docker}"|grep -v libpthread|grep -v libc.so|awk '{print $3}'|egrep '^/'; )
        )\
        -v "${docker}:${docker}" \
        -v "/sys/fs/cgroup:/sys/fs/cgroup:ro" \
        -v "/var/lib/docker:/var/lib/docker" \
        -v "/var/run/docker:/var/run/docker" \
        -v "/var/run/docker.sock:/var/run/docker.sock" \
        -v "/:/HOST_ROOTFS" \
        -v "$W:$W" \
        $( if [[ "$W" != "$CW" ]];then echo " -v ${CW}:${CW}"; fi) \
        -e IMAGES="$IMAGES" \
        "corpusops/ubuntu:14.04" \
        bash -c 'while true;do sleep 65200;done'
    if [[ $? != 0 ]];then
        log "TESTRUNNER controller: $runner failed to spawn"
        exit 1
    else
        log "TESTRUNNER controller: $runner spawned"
    fi
    runnerid=$(get_runner_id)
}

run_test() {
    local role=$1
    if [ -e "$role/.travis.env" ];then
        log "Load env for $role"
        . "$role/.travis.env"
    fi
    log "Testing $role"
    if [[ -z "${NOT_IN_DOCKER-}" ]]; then
        if ! ( vv sudo docker exec $runnerid bash -c \
               "if ! $COPS_ROOT/hacking/test_roles "'"'"${role}"'"'"; then
                  echo 'First test try failed, try to update code and retry test' >&2;
                  $COPS_ROOT/bin/install.sh -s && $COPS_ROOT/hacking/test_roles "'"'"${role}"'"'"
                fi" \
           ); then
             ret=1;
        else
            ret=0;
        fi
    else
        log 'NOT_IN_DOCKER is set, skip tests in docker (baremetal tests)' >&2
        if [ ! -e "$COPS_ROOT/venv/bin/ansible" ];then
            log "Installing corpusops on baremetal"
            if ! ( \
              sudo echo docker cp "$runnerid:$(dirname $COPS_ROOT)"/ "$(dirname $(dirname $COPS_ROOT))"/ &&\
              sudo docker cp "$runnerid:$(dirname $COPS_ROOT)"/ "$(dirname $(dirname $COPS_ROOT))"/ &&\
              sudo rm -rf "$COPS_ROOT"/venv/{bin,include,lib,local} &&\
              sudo $COPS_ROOT/bin/install.sh -C -S; ); then
                log "Failure to install corpusops"
                ret=3
            fi
        fi
        if [[ $ret -le 1 ]];then
            set -x
            if ! sudo -E $COPS_ROOT/hacking/test_roles "${role}"; then
                echo 'BM: First test try failed, try to update code and retry test' >&2;
                vv sudo -E $COPS_ROOT/bin/install.sh -s;
                if ! sudo -E $COPS_ROOT/hacking/test_roles "${role}";then
                    ret=2;
                else
                    ret=0;
                fi
            else
                ret=0;
            fi
        fi
    fi
}

cd "${W}"
ROLES=${@-}
FROM_HISTORY=${FROM_HISTORY:-${TRAVIS}}
FROM_COMMIT=${FROM_COMMIT:-HEAD^}
TO_COMMIT=${TO_COMMIT:-HEAD}
if [[ -z $ROLES ]];then
    candidates=""
    if [[ -n ${FROM_HISTORY} ]];then
        if ! ( git diff -q --exit-code >/dev/null 2>&1 );then
            log "WC not clean using diff status"
            for i in $(git diff --name-only|grep "/"|sed -re "s#/.*##g"|uniq);do
                candidates="$candidates $i"
            done
        else
            if git show -q HEAD | egrep -q "fulltest|alltest";then
                log "Using default (all tests)"
            else
                debug "Searching in diff what did changed"
                for i in $( \
                    git diff --name-only ${FROM_COMMIT}..${TO_COMMIT}\
                    |grep "/"|sed -re "s#/.*##g"|uniq);do
                    candidates="$candidates $i"
                done
            fi
        fi
    fi
    for candidate in $candidates;do
        r="$W/$candidate"
        if is_role "$r";then
            ROLES="$ROLES $r"
        fi
    done
fi
if [[ -z $ROLES ]];then
    ROLES=${ALL_ROLES}
fi
FROM_HISTORY=${FROM_HISTORY:-${TRAVIS}}
if [[ -n $DRY_RUN ]];then
    log "Testing $ROLES"
    exit 0
fi
do_trap post_tests_cleanup EXIT
post_tests_cleanup
setup
# no test == failure
# then if at least one test fail, we fail
ret=-1
for r in $ROLES;do
    if ! ( run_test "$r"; );then
        ret=6
    else
        if [[ $ret == -1 ]];then ret=0;fi
    fi
done
exit ${ret}
# vim:set et sts=4 ts=4 tw=80:
