#!/usr/bin/env bash
# {{ansible_managed}}
if [ "x${DEBUG}" != "x" ];then set -x;fi
log() { echo "$@" >&2;  }
# {% set d = corpusops_localsettings_certbot_vars %}
W="$(dirname $(readlink -f "$0"))"
REPO="{{d.repo_dir}}"
GIT_URL="{{d.git_url}}"
certsd="{{d.configdir}}/live"
owner="{{d.user}}"
group="{{d.group}}"
TIP="${TIP:-"certsremote/master"}"
if [ ! -e "$REPO" ];then
    log "REPO certs dir $REPO doesnt exists, creating it"
    mkdir -p "$REPO"
    chown "$owner:$group" "$REPO"
    chmod o-rwx "$REPO"
fi
set -e
cd "$REPO"
if [ ! -e .git ];then git init . &>/dev/null ;fi
git remote rm certsremote  &>/dev/null || /bin/true
git remote add certsremote "$GIT_URL"
git config --remove-section user  &>/dev/null || /bin/true
git config user.email 'cert@certs.com'
git config user.name 'certs'
git fetch certsremote &>/dev/null
git reset --hard $TIP &>/dev/null
exit $?
# vim:set et sts=4 ts=4 tw=0:
