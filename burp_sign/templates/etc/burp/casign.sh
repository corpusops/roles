#!/usr/bin/env bash
# {% set data = cops_burpsign_vars %}
set -e
if [ "x$DEBUG" != "x" ];then set -x;fi
changed() { echo "CHANGED $@">&2; }
pref="{{data.prefix}}"
c="{{data.ca_conf}}"
ca="{{data.ca}}"
burp_ca="burp_ca --config $c -d $ca"
burp_cag="burp_ca --config $c -d $ca/gen"
cacn="burpCA"
cname="${1:-"$(hostname -f)"}"
if [ "x$cname" = "x" ];then echo "missing CN, provide at least one";exit 1;fi
if [ ! -e "$ca" ];then
    mkdir -p "$ca"
    changed dir
fi
if [ ! -e "$ca/CA_$cacn.crt" ] || [ ! -e "$ca/CA_$cacn.key" ] ;then
    rm -rf "$ca/gen/"
    $burp_cag --batch --ca "$cacn" -n "$cacn" --days 365000 -D 365000 -i
    ( cd "$ca/gen" && cp -rf . $ca )
    changed init-ca
fi
for cname in $@;do
    if [ ! -e "$ca/$cname.key" ];then
        $burp_ca --batch --key --name "$cname"
        changed key
    fi
    if [ ! -e "$ca/$cname.csr" ];then
        $burp_ca --batch --request --name "$cname"
        changed csr
    fi
    if [ ! -e "$ca/$cname.crt" ];then
        $burp_ca --batch --days 365000 --sign --ca "$cacn" --name "$cname"
        changed sign-crt
    fi
done
# vim:set et sts=4 ts=4 tw=80:
