#!/usr/bin/env bash
#
# This script remove/reset parts of a container to impersonate it
#
# Those vars can control to no wipe some parts of a snapshotted container
# * NO_PROJECTS_ARCHIVES_WIPE
# * NO_SSL_WIPE
# * NO_FIREWALL_WIPE
# * NO_HISTORIES_WIPE
# * NO_SSHD_WIPE
# * NO_ACLS_BACKUP
# * NO_ETCKEEPER_WIPE
# * NO_RECREATE
# * NO_REMOVE
# * NO_WIPE
# * NO_SSHKEYS_WIPE
# * NO_SSHHOME_WIPE
# * NO_FILE_WIPE
#

set -e
if [ "x${DEBUG}" != "x" ];then set -x;fi

is_docker=""
for i in /.dockerinit /.dockerenv;do
    if [ -f "${i}" ];then
        is_docker="1"
        break
    fi
done
is_this_docker() {
    if [ "x${is_docker}" != "x" ];then
        return 0
    else
        if grep -q "system.slice/docker-" /proc/1/cgroup 2>/dev/null;then
            is_docker="1"
            return 0
        fi
        return 1
    fi
}

# remove totally
REMOVE="
/etc/lxc_reset_done
/tmp/.saltcloud
/root/.cache
/srv/makina-states/var/
/home/*/.cache
"
# directories to empty out or files to wipe content from
WIPE="
/tmp
/var/tmp
/var/log/unattended-upgrades/
/var/log/*.1
/var/log/*.0
/var/log/*.gz
"
# files to delete
FILE_REMOVE="
/var/cache/apt/archives/
/var/lib/apt/lists
"
FILE_WIPE="
/var/log
"
# salt cache is relying on semi hardlinks, deleting files from their orig
# just delete/create the caches is sufficient
TO_RECREATE=""

FIND_EXCLUDES="/mnt|/HOST_(CWD|(ROOT)*FS)|.*lib/(lxc|docker).*"

# wipe various histories
if [[ -z "${NO_HISTORIES_WIPE-}" ]];then
    while read fic;do
        WIPE="${WIPE}
${fic}
"
    done < \
        <( find /root /home /var \
            \( -regextype posix-extended -regex "${FIND_EXCLUDES}"  -prune \) \
            -o \( -name .bash_history -or -name .viminfo \) -print)
fi


if [[ -z "${NO_SSL_WIPE-}" ]];then
    WIPE="${WIPE}
/usr/local/share/ca-certificates/
/etc/ssl/apache
/etc/ssl/cloud
/etc/ssl/cloud2
/etc/ssl/nginx
"
fi

if [[ -z "${NO_SSHD_WIPE-}" ]];then
    WIPE="${WIPE}
/etc/ssh/ssh_host*key
/etc/ssh/ssh_host*pub
"
fi


if [[ -z "${NO_PROJECTS_ARCHIVES_WIPE-}" ]];then
    # in dockers, strip projects archives
    if is_this_docker;then
        set +e
        while read i;do
            rm -rf "${i}" || /bin/true
        done < \
            <( find /srv/projects/*/archives -mindepth 1 -maxdepth 1 \
            \( -regextype posix-extended -regex "${FIND_EXCLUDES}"  -prune \) \
            -o \( -type d \) -print 2>/dev/null)
    fi
fi


if [[ -z "${NO_RECREATE-}" ]];then
    while read i;do
        if [ "x${i}" != "x" ];then
            if [ ! -h "${i}" ];then
                if [ -f "${i}" ];then
                    rm -fv "${i}" || /bin/true
                    touch "${i}" || /bin/true
                elif [ -d "${i}" ];then
                    rm -rv "${i}" || /bin/true
                    mkdir -v "${i}" || /bin/true
                fi
            fi
        fi
    done <<< "${TO_RECREATE}"
fi


if [[ -z "${NO_REMOVE-}" ]]; then
    for i in ${REMOVE};do
        if [ -d "${i}" ];then
            rm -vrf "${i}" || /bin/true
        fi
        if [ -h "${i}" ] || [ -f "${i}" ];then
            rm -vf "${i}" || /bin/true
        fi
    done
fi


if [[ -z "${NO_WIPE-}" ]]; then
    while read i;do
        if [ "x${i}" != "x" ];then
            while read k;do
                if [ -h "${k}" ];then
                    rm -fv "${k}" || /bin/true
                elif [ -f "${k}" ];then
                    while read fic;do rm -fv "${fic}" || /bin/true;done < \
                        <( find "${k}" \
                        \( -regextype posix-extended -regex "${FIND_EXCLUDES}"  -prune \) \
                        -o -type f -print 2>/dev/null )
                elif [ -d "${k}" ];then
                    while read j;do
                        if [ ! -h "${j}" ];then
                            rm -vrf "${j}" || /bin/true
                        else
                            rm -vf "${j}" || /bin/true
                        fi
                    done < \
                        <( find "${k}" -mindepth 1 -maxdepth 1 \
                        \( -regextype posix-extended -regex "${FIND_EXCLUDES}"  -prune \) \
                        -o -type d -print 2>/dev/null )
                    while read j;do
                        rm -vf "${j}" || /bin/true
                    done < \
                        <( find "${i}" -mindepth 1 -maxdepth 1 \
                        \( -regextype posix-extended -regex "${FIND_EXCLUDES}"  -prune \) \
                        -o -type f -print 2>/dev/null)
                fi
            done < <(ls -1 ${i} 2>/dev/null)
        fi
    done <<< "${WIPE}"
fi


# special case, log directories must be in place, but log resets
if [[ -z "${NO_FILE_REMOVE-}" ]];then
    while read i;do
        if [ "x${i}" != "x" ];then
            while read f;do rm -f "${f}" || /bin/true;done < \
                <( find "${i}" \
                \( -regextype posix-extended -regex "${FIND_EXCLUDES}"  -prune \) \
                -o -type f -print 2>/dev/null )
        fi
    done <<< "${FILE_REMOVE}"
fi


if [[ -z "${NO_FILE_WIPE-}" ]];then
    while read i;do
        if [ "x${i}" != "x" ];then
            while read f;do echo > "${f}" || /bin/true;done < \
                <( find "${i}" \
                \( -regextype posix-extended -regex "${FIND_EXCLUDES}"  -prune \) \
                -o -type f -print 2>/dev/null )
        fi
    done <<< "${FILE_WIPE}"
fi


# reset shorewall settings if a,y
if [[ -z "${NO_FIREWALL_WIPE-}" ]];then
    while read i;do
        sed -i -re "s/ACCEPT.? +net:?.*fw +-/ACCEPT net fw/g" "$i" || /bin/true
    done < <( find /etc/shorewall/rules -type f 2>/dev/null )
fi


# wipe various SSH setttings
if [[ -z "${NO_SSHHOME_WIPE-}" ]];then
    while read i;do
        echo "WIPING $i"
        if [ -d "${i}" ];then
            pushd "${i}" 1>/dev/null 2>&1
            for i in config authorized_keys authorized_keys2;do
                if [ -f "${i}" ];then echo >"${i}";fi
            done
            while read f;do rm -vf "${f}";done < \
                <( ls -1 known_hosts 2>/dev/null )
            if [[ -z "${NO_SSHKEYS_WIPE-}" ]];then
                while read f;do rm -vf "${f}";done < \
                    <( ls -1 id_* 2>/dev/null )
            fi
            popd 1>/dev/null 2>&1
        fi
    done < <( find / \
           \( -regextype posix-extended -regex "${FIND_EXCLUDES}" -prune \) \
           -or -name .ssh -print )
fi

# reset etckeeper
if [[ -z "${NO_ETCKEEPER_WIPE-}" ]];then
    if [ -e /etc/.git ] && [ -e /usr/bin/etckeeper ];then
        rm -rf /etc/.git
        etckeeper init || /bin/true
        cd /etc
        git config user.name "name"
        git config user.email "a@b.com"
        etckeeper commit "init" || /bin/true
    fi
fi

# save current posix acls
if [[ -z "${NO_ACLS_BACKUP-}" ]];then
    if hash -r getfacl 1>/dev/null 2>/dev/null;then
        getfacl -s -R / > /acls.txt || /bin/true
        if [ -e /acls.txt ];then
            xz -f -z -9e /acls.txt || /bin/true
        fi
    fi
fi
# vim:set et sts=4 ts=4 tw=80:
