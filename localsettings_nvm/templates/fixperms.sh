#!/usr/bin/env bash
cd "$(dirname $(readlink -f "$0"))"
TOPDIR="$(pwd)"
user="$(stat -c "%u" .)"
group="$(stat -c "%g" .)"
while read i;do
    echo "fixperms for $i" >&2
    if [ ! -h "${i}" ];then
      if [ -d "${i}" ];then
        chmod g-s "${i}"
        chown $user:$group "${i}"
        chmod g+w "${i}"
        chmod g+s "${i}"
      elif [ -f "${i}" ];then
        chown $user:$group "${i}"
        chmod g+w "${i}"
      fi
    fi
done < <( \
 find -H \
    "$TOPDIR" \
 \(\
    \( -type f -and \( -not -user $user -or -not -group $group \) \)\
    -or \( \
       -type d -and \( -not -user $user -or \
                       -not -group $group -or \
                       -not -perm -2000 \) \
    \)\
 \) )
# vim:set et sts=4 ts=4 tw=80:
