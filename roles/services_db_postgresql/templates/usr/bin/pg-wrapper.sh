#!/usr/bin/env bash
#{{ ansible_managed}}
bin="$1"
binary="$(which $bin 2>/dev/null)"
version={{corpusops_services_db_postgresql_version}}

has_command() {
    ret=1
    if which which >/dev/null 2>/dev/null;then
      if which "${@}" >/dev/null 2>/dev/null;then
        ret=0
      fi
    else
      if command -v "${@}" >/dev/null 2>/dev/null;then
        ret=0
      else
        if hash -r "${@}" >/dev/null 2>/dev/null;then
            ret=0
        fi
      fi
    fi
    return ${ret}
}


die() {
    echo $@
    exit 1
}
# get pgsql pid
pid=$(ps aux|grep "$version/bin/postgres"|grep -v grep|awk '{print $2}')
if [[ -z $pid ]];then
    die "$version: invalid pid"
fi
# from the pid, get the running port
socket_path=
if has_command netstat;then
	socket_port=$(netstat -pnlt 2>/dev/null|grep $pid|grep -v tcp6|awk '{print $4}'|awk -F: '{print $2}')
elif [ -e /proc/$pid/net/unix ];then
    socket_path=$(grep postgresql /proc/$pid/net/unix|awk '{print $NF}')
else
	socket_port=5432
fi
if [[ -z $socket_path ]];then
    if [[ -z $socket_port ]];then
        die "$version: invalid socket port"
    fi
    socket_path="/var/run/postgresql/.s.PGSQL.$socket_port"
fi
if [[ ! -e "$binary" ]];then
    die "$version: invalid binary: $bin"
fi
if [[ ! -e "$socket_path" ]];then
    die "$version: invalid socket path: $socket_path"
fi
export PGHOST="/var/run/postgresql"
export PGPORT="$socket_port"
shift
export PATH=/usr/lib/postgresql/$version/bin:$PATH
exec $binary $@
