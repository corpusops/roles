#!/usr/bin/env bash
{% set data=cops_burpclient_vars %}
NAME={{data.name}}
set -e
if [ "x${SDEBUG-}" != "x" ];then set -x;fi
export TPID=$$
export PATH="$W:$PATH"
export W=$(cd "$(dirname $0)" && pwd)
export PS="ps"
export TIMEOUT=$((60*60*24*2))
export LOCK="/var/run/burp-client-${NAME}.cron.lock"
export PIDFILE="/var/run/burp.client-${NAME}.pid"
is_container() {
    cat -e /proc/1/environ 2>/dev/null|grep -q container=
    echo "${?}"
}
filter_host_pids() {
    pids=""
    if [ "x$(is_container)" = "x0" ];then
        pids="${pids} $(echo "${@}")"
    else
        for pid in ${@};do
            if [ "x$(grep -q /lxc/ /proc/${pid}/cgroup 2>/dev/null;echo "${?}")" != "x0" ];then
                pids="${pids} $(echo "${pid}")"
            fi
         done
    fi
    echo "${pids}" | sed -e "s/\(^ \+\)\|\( \+$\)//g"
}
burp_client() {
    ( ( ps_etime|sort -n -k2|grep burp|grep -- " -a t"|grep $W|grep -v grep ) || true;\
      ( ps_etime|sort -n -k2|grep cron|grep $W|grep -v grep|grep -vE "[0-9]+\s+0\s+"  ) || true ) \
    | sort | uniq
}
ps_etime() {
    ${PS} -eo pid,comm,etime,args | perl -ane '@t=reverse(split(/[:-]/, $F[2])); $s=$t[0]+$t[1]*60+$t[2]*3600+$t[3]*86400;$cmd=join(" ", @F[3..$#F]);print "$F[0]\t$s\t$F[1]\t$F[2]\t$cmd\n"'
}
kill_() {
    for i in $@;do if [ "x$i" != "x$TPID" ] || [ "x$i" = "x0" ];then echo "Killing $i" >&2;kill -9 $i || true;fi;done
}
kill_old_syncs() {
    # kill all stale synchronnise code jobs
    while read psline;do
        pid="$(filter_host_pids $(echo $psline|awk '{print $1}'))"
        boottime=$(cat /proc/stat  | awk '/btime/ { print $2 }')
        statf=/proc/$pid/stat
        if [ "x${pid}" != "x" ] && [ -e $statf ];then
            starttime_from_boot=$(awk '{print int($22 / 100)}' $statf)
            starttime=$((boottime + starttime_from_boot))
            seconds=$((now - starttime))
            # 8 minutes
            if [ "${seconds}" -gt "$TIMEOUT" ];then
                echo "Something was wrong with last backup ($seconds vs $TIMEOUT), killing old sync processes: $pid"
                echo "${psline}"
                kill_ "${pid}"
                cleanup="y"
            fi
        fi
    done < <( burp_client )
    if [ "x$(burp_client|wc -l|sed 's/ +//g')" = "x0" ];then
        if [ -f $PIDFILE ];then
            cleanup="y"
            rm -f "$PIDFILE"
        fi
    fi
    if [ -e "$LOCK" ];then
        starttime=$(stat --format="%W" "$LOCK")
        seconds=$((now - starttime))
        # 8 minutes
        if [ "${seconds}" -gt "$TIMEOUT" ];then
            echo "Something was wrong, lockfile is pretty old ($seconds vs $TIMEOUT)"
            kill_ $(burp_client|awk '{print $2}')
            remove_lock
        fi
    fi
}
remove_lock() {
    if [ -e $LOCK ];then echo "Rmoving $LOCK"; rm -f "$LOCK";fi
}
run_burp () {
    if [ -f burp.sh ];then
        burp.sh -a t
    else
        burp -a t -c "$W/burp-client.conf"
    fi
}
cleanup=""
now="$(date +%s)"
kill_old_syncs
if [ -e "$LOCK" ];then echo "$W is locked ($LOCK)";exit 0;fi
touch "$LOCK"
ret=0;if ! ( run_burp );then ret=1;fi
remove_lock
exit $ret
# vim:set et sts=4 ts=4 tw=0:
