#!/usr/bin/env bash
# export certbot data to formats for other daemons (nginx, haproxy)
# {{ansible_managed}}
if [ "x${DEBUG}" != "x" ];then set -x;fi
W="$(dirname $(readlink -f "$0"))"
log() { echo "$@" >&2;  }
# {% set d = corpusops_localsettings_certbot_vars %}
REPO="{{d.repo_dir}}"
GIT_URL="{{d.git_url}}"
certsd="{{d.configdir}}/live"
owner="${CERTBOT_OWNER:-{{d.user}}}"
group="${CERTBOT_GROUP:-{{d.group}}}"
rsynco="-a --delete -kL"
if [ ! -e "$REPO" ];then
    log "REPO certs dir $REPO doesnt exists, creating it"
    mkdir -p "$REPO"
    chown "$owner:$group" "$REPO"
    chmod o-rwx "$REPO"
fi
set -e
cd "$REPO"
if [ -e "$certsd" ];then rsync $rsynco "${certsd}/" live/;fi
if [ ! -e .git ];then git init .;fi
if [ -e "$W/le_haproxy.sh" ];then
    SKIP_INSTALL="" SKIP_RELOAD="y" \
        HAPROXY_CERTS_DIR="$REPO/haproxy" \
        CERTBOT_LIVE_DIR="$REPO/live" \
        "$W/le_haproxy.sh"
fi
for i in haproxy live;do if [ -e $i ];then touch $i/.empty;git add -f "$i/"*;fi;done
git remote rm  origin || /bin/true
git remote add origin "$GIT_URL"
git config --remove-section user || /bin/true
git config user.email 'cert@certs.com'
git config user.name 'certs'
if ! ( git diff --exit-code &>/dev/null );then git commit -am "up";fi
if ! ( git diff --cached --exit-code &>/dev/null );then git commit -am "up";fi
if ( echo "$GIT_URL" | grep -E -q 'ssh://([^/]+)/(.*)' );then
    ssh_host="$(echo "$GIT_URL" | sed -re 's|^ssh://([^/]+)(/.*)|\1|g' )"
    ssh_path="$(echo "$GIT_URL" | sed -re 's|^ssh://([^/]+)(/.*)|\2|g' )"
    if ! ( ssh $ssh_host test -e "$ssh_path" );then
        ssh $ssh_host git init --bare "$ssh_path"
    fi
fi
git push --force origin HEAD:master
# vim:set et sts=4 ts=4 tw=0:
