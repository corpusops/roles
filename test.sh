#!/usr/bin/env bash
# Either test on docker if possible or directly on travis compute node
. test_env.sh

# SYNC_CORPUSOPS=y IMAGES=corpusops/ubuntu:16.04 FORCE_PULL=y DEBUG=1
#   FORCE_SYNC=y ./test.sh corpusops.roles/actionhelper/


LOCAL_COPS_ROOT="${LOCAL_COPS_ROOT:-$CW/local/corpusops.bootstrap}"

RED="\\e[0;31m"
CYAN="\\e[0;36m"
YELLOW="\\e[0;33m"
NORMAL="\\e[0;0m"
if [[ -n ${NOCOLORS-${NOCOLOR-}} ]];then
    RED=""
    CYAN=""
    YELLOW=""
    NORMAL=""
fi

log() { echo -e "$@">&2; }


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

spawn_controller() {
    if [[ -z ${DOCKER_NO_PULL-} ]];then
        for img in $CONTROLLER_IMAGE;do
            vvv sudo "$docker" pull "$img"
            die_in_error "pull $img failed"
        done
    fi
    vvv sudo "$docker" run -ti -d --name=$runner \
        $( while read v; do echo " -v ${v}:${v}:ro";done < \
          <( ldd "${docker}" \
              | egrep -v "libc.so|libpthread.so|libdl.so" \
              | awk '{print $3}'|egrep '^/'; )
        )\
        -v "${docker}:${docker}" \
        -v "/sys/fs/cgroup:/sys/fs/cgroup:ro" \
        -v "/var/lib/docker:/var/lib/docker" \
        -v "/var/run/docker:/var/run/docker" \
        -v "/var/run/docker.sock:/var/run/docker.sock" \
        --tmpfs /run/lock --tmpfs /run \
        -v "/:/HOST_ROOTFS" \
        -v "$W:$W" \
        $( if [[ "$W" != "$CW" ]];then echo " -v ${CW}:${CW}"; fi) \
        -e IMAGES="${IMAGES}" \
        "$CONTROLLER_IMAGE" \
        bash -c 'while true;do sleep 65200;done'
    if [[ $? != 0 ]];then
        log "TESTRUNNER controller: $runner failed to spawn"
        exit 1
    else
        log "TESTRUNNER controller: $runner spawned"
    fi
}

install_cached_corpusops() {
    ret=0
    if ( [[ -n "${FORCE_INSTALL_LOCAL_COPS-}" ]] ||\
         [[ -n "${FORCE_REINSTALL_LOCAL_COPS-}" ]] ) || \
       [ ! -e "$LOCAL_COPS_ROOT/venv/bin/ansible" ];then
        log "Installing corpusops on baremetal"
        vv docker exec -ti $runner sh -c\
            'if [ ! -e '"$LOCAL_COPS_ROOT"' ];then mkdir -p '"$LOCAL_COPS_ROOT"';fi' &&\
        vv docker exec -ti $runner \
            rsync -a --exclude=venv/{bin,include,lib,local,man} \
            --exclude="corpusops_use_venv" \
            $COPS_ROOT/ $LOCAL_COPS_ROOT/ &&\
        vv docker exec -ti $runner \
            chown -R $IDWHOAMI $LOCAL_COPS_ROOT && \
        if [[ -n "${FORCE_REINSTALL_LOCAL_COPS-}" ]] || [ ! -e "$LOCAL_COPS_ROOT/venv/bin/ansible" ];then
            "$LOCAL_COPS_ROOT/bin/install.sh" -C -S
        fi
        ret=$?
    fi &&\
    if [[ $ret = 0 ]] && [[ -n "$FORCE_SYNC" ]];then
        echo "Sync corpusops from origin"
        ( cd "$LOCAL_COPS_ROOT" && bin/install.sh -C -s; )
    fi &&\
    if [[ -n "$FORCE_PULL" ]];then
        echo "Sync corpusops from origin (only bootstrap)"
        ( cd "$LOCAL_COPS_ROOT" && \
          gargs=$(if [ "x$(git config user.email)" = "x" ];then \
            echo "-c user.name=Corpusops -c user.email=autocommiter@corpousops" \
          fi) && \
          git $gargs pull; )
    fi &&\
    if [[ -n "${SYNC_CORPUSOPS-}" ]];then
        log "Sync back local corpusops tree to image"
        vv docker exec -ti $runner \
            rsync -a --exclude=venv/{bin,include,lib,local,man} \
            --exclude="*corpusops_use_venv" \
            "$LOCAL_COPS_ROOT/" "$COPS_ROOT/"
    fi
    ret=$?
    if [[ $ret != 0 ]]; then
        log "Failure to setup corpusops"
        ret=3
    fi
    return $ret
}

respawn_controller() {
    vv docker rm -f $runner && spawn_controller
}

setup() {
    spawn_controller
    die_in_error "Failure to spawn controller"
    install_cached_corpusops
    die_in_error "Bailing out, failure to setup corpusops"
    if [[ -n ${DOCKER_UPGRADE} ]];then
            sudo -E bash << EOF
              set -x
              service docker stop &&\
              $LOCAL_COPS_ROOT/bin/silent_run \
               $LOCAL_COPS_ROOT/bin/cops_apply_role \
                $LOCAL_COPS_ROOT/roles/corpusops.roles/services_virt_docker/role.yml
EOF
        die_in_error "docker upgrade"
        respawn_controller
    fi
    runnerid=$(get_runner_id)
    if [[ -z $runnerid ]];then
        log "container for $runner not found"
        exit 1
    fi
}

run_test_() {
    local roles=$@
    while read role;do
        if [[ -n $role ]] && [ -e "$role/.travis.env" ];then
            log "Load env for $role"
            . "$role/.travis.env"
        fi
    done <<< "$roles"
    log "Testing $roles"
    if [[ -n "${NOT_IN_DOCKER-}" ]]; then
        log 'NOT_IN_DOCKER is set, skip tests in docker (baremetal tests)' >&2
    fi
    if ! sudo -E "$LOCAL_COPS_ROOT/bin/silent_run" \
        "$LOCAL_COPS_ROOT/hacking/test_roles" "${roles}"; then
        echo 'BM: First test try failed, try to update code and retry test' >&2;
        vv "$LOCAL_COPS_ROOT/bin/install.sh" -C -s;
        if ! sudo -E "$LOCAL_COPS_ROOT/bin/silent_run" \
            "$LOCAL_COPS_ROOT/hacking/test_roles" "${roles}";then
            ret=2;
        else
            ret=0;
        fi
    else
        ret=0;
    fi
}

run_test() { ( run_test_ "${@}"; ) }


cd "${W}"
ROLES=${TEST_ROLES-${@-}}
TEST_VARS_ROLES=${TEST_VARS_ROLES:-${TRAVIS}}
FROM_HISTORY=${FROM_HISTORY:-${TRAVIS}}
USE_LOCAL_DIFF="${USE_LOCAL_DIFF-1}"
FROM_COMMIT=${FROM_COMMIT:-HEAD^}
TO_COMMIT=${TO_COMMIT:-HEAD}
SKIP_REDO_VENV=${SKIP_REDO_VENV-}
IMAGES="$(echo $IMAGES|xargs -n1)"
if [[ -z "${ROLES}" ]] && [[ -n "${USE_LOCAL_DIFF}" ]] \
    && ! ( git diff -q --exit-code >/dev/null 2>&1 );then
    candidates=""
    log "WC not clean using diff status"
    for i in $(git diff --name-only|grep "/"|sed -re "s#/.*##g"|awk '!seen[$0]++');do
        candidates="$candidates $i"
    done
    for candidate in $candidates;do
        r="$W/$candidate"
        if is_role "$r";then ROLES="$ROLES $r";fi
    done
fi
if [[ -z "${ROLES}" ]];then
    if [[ -n "${FROM_HISTORY}" ]];then
        candidates=""
        if git show -q HEAD | egrep -q "fulltest|alltest";then
            log "Using default (all tests)"
        else
            debug "Searching in diff what did changed: ${FROM_COMMIT}..${TO_COMMIT}"
            for i in $( \
                git diff --name-only ${FROM_COMMIT}..${TO_COMMIT}\
                | grep "/"| sed -re "s#/.*##g"| awk '!seen[$0]++');do
                candidates="$(printf "$candidates\n$i\n")"
            done
        fi
        for candidate in $candidates;do
            r="$W/$candidate"
            if is_role "$r";then ROLES="$(printf "$ROLES\n$r\n")";fi
        done
    fi
fi
ROLES_VARS=""
if [[ -n "${TEST_VARS_ROLES}" ]];then
    while read candidate;do
        r="$W/$candidate"
        if is_role "$r";then
            ROLES_VARS="$(printf "$ROLES_VARS\n$(cd "$r" && pwd)")"
		fi
    done < <( \
        find -maxdepth 1 -mindepth 1 -type d -name '*vars' \
        | sort \
        | egrep -v 'include_jinja_vars|lxc_vars': )
fi
ROLES="$(printf "$ROLES\n"|xargs -n1|awk '!seen[$0]++')"
ROLES_VARS="$(printf "$ROLES_VARS\n"|xargs -n1|awk '!seen[$0]++')"
ROLES_TO_TEST="$(printf "$ROLES_VARS\n$ROLES\n"|xargs -n1|awk '!seen[$0]++')"
if [[ -n $DRY_RUN ]];then
    log "${CYAN}Testing${NORMAL}"
    if [[ -n $ROLES_TO_TEST ]];then
        log "${YELLOW}$(echo "$ROLES_TO_TEST"|sed "s/^/ - /g")${NORMAL}"
    else
        log "${YELLOW}No tests found${NORMAL}"
    fi
    exit 0
fi
do_trap post_tests_cleanup EXIT
post_tests_cleanup
setup

# no test == failure
# then if at least one test fail, we fail
if [[ -n "$ROLES_VARS" ]];then
    run_test "$ROLES_VARS"
fi
ret_vars=$?
if [[ -n "$ROLES" ]];then
    run_test "$ROLES"
fi
ret_roles=$?
if [[ ${ret_roles} != 0 ]];then
    log "${GREEN}Vars tests failed${NORMAL}"
    ret=56
fi
if [[ ${ret_vars} != 0 ]];then
    log "${RED}Roles tests failed${NORMAL}"
    ret=57
fi
exit ${ret}
# vim:set et sts=4 ts=4 tw=0:
