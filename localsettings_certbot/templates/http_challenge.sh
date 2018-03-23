#!/usr/bin/env bash
# {{ansible_managed}}
# {% set d = corpusops_localsettings_certbot_vars %}
if [ "x${DEBUG}" != "x" ];then set -x;fi
log() { echo "$@" >&2;  }
get_command() {
    local p=
    local cmd="${@}"
    if which which >/dev/null 2>/dev/null;then
        p=$(which "${cmd}" 2>/dev/null)
    fi
    if [ "x${p}" = "x" ];then
        p=$(export IFS=:;
            echo "${PATH-}" | while read -ra pathea;do
                for pathe in "${pathea[@]}";do
                    pc="${pathe}/${cmd}";
                    if [ -x "${pc}" ]; then
                        p="${pc}"
                    fi
                done
                if [ "x${p}" != "x" ]; then echo "${p}";break;fi
            done )
    fi
    if [ "x${p}" != "x" ];then
        echo "${p}"
    fi
}
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
for i in dig ip;do
    if ! ( has_command $i; );then
        echo "install $i (dnsutils or iproute2)"
        exit 1
    fi
done
chrono=$(date "+%F-%T")
CERTBOT="${CERTBOT:-$(get_command certbot)}"
failed=""
dnsmismatch=""
DNS_SERVER="${DNS_SERVER:-{{d.dns_server}}}"
EXPIRY={{d.expiry}}
exp_limit={{d.days}}
CERTBOT_CONFIGDIR="${CERTBOT_CONFIGDIR:-{{d.configdir}}}"
CERTBOT_WORKDIR="${CERTBOT_WORKDIR:-{{d.workdir}}}"
CONFIG="${CERTBOT_CONFIG:-{{d.config}}}"
local_ips="$(ip -o addr \
            | awk '!/^[0-9]*: ?lo|link\/ether/ {print $4}'\
            | sed -e "s/\/.*//g")"
CERTBOT_IPS="${CERTBOT_IPS:-"
{{corpusops_network_live_ext_ip}}
$local_ips
"}"
CERTBOT_DOMAINS="${CERTBOT_DOMAINS:-"{{d.domains|join('\n')}}"}"
updated=""
cli_args="{{d.certonly_args.replace('\n', '')}}"
while read domain;do
	cert_file="$CERTBOT_CONFIGDIR/live/$domain/fullchain.pem"
	key_file="$CERTBOT_CONFIGDIR/live/$domain/privkey.pem"
	force="${FORCE_RENEW-}"
	# check if exposed public ip is tied to the requested domain
	ip=$(dig  +short      "$domain" @$DNS_SERVER)
	ip6=$(dig +short AAAA "$domain" @$DNS_SERVER)
    ipfound=
    force_args="${FORCE_ARGS-}"
    # force_args="--force-renewal"
    while read dnsip;do
        while read localip;do
            if [ "x${dnsip}" != "x" ] && [ "x$dnsip" = "x$localip" ];then
                ipfound=1
                break
            fi
        done <<< "$CERTBOT_IPS"
        if [ "x${ipfound}" != "x" ];then break;fi
    done <<< "$ip
$ip6"
	if [ "x${ipfound}" = "x" ];then
        :
	elif [ ! -f "$cert_file" ]; then
		log "certificate file not found for domain $domain." >&2
		force=1
	else
		exp=$(date -d "$(openssl x509 -in $cert_file -text -noout\
			|grep "Not After"|cut -c 25-)" +%s)
		datenow=$(date -d "now" +%s)
		days_exp=$(echo \( $exp - $datenow \) / $EXPIRY |bc)
	fi
	if [ "x${ipfound}" = "x" ];then
        log "DNS setup is dnsmismatch for $domain"
        dnsmismatch="$dnsmismatch $domain"
	elif [ "x${force}" = "x" ] && [ $days_exp -gt $exp_limit ] ; then
		msg="The certificate for $domain is up to date,"
        msg="$msg no need for renewal ($days_exp days left)."
        log $msg
	else
		echo "Starting Let's Encrypt renewal script for $domain..."
        if [ -e "$CERTBOT_CONFIGDIR/archive/${domain}" ];then
            tar cjvf $domain-bck-${chrono}.tbz2 \
                $(find "$CERTBOT_CONFIGDIR/"{live,renewal,archive}/{${domain},${domain}.conf} -maxdepth 0 -mindepth 0) &&\
            rm -rvf "$CERTBOT_CONFIGDIR/"{live,renewal,archive}/{${domain},${domain}.conf}
        fi
		if ! ( $CERTBOT certonly $force_args $cli_args -d $domain; );then
			failed="$failed $domain"
			break
        else
            updated="$updated $domain"
		fi
	fi
done <<< "$CERTBOT_DOMAINS"
if [[ -n "$dnsmismatch" ]];then
	log "certbot dns mismatch domains: $dnsmismatch" >&2
fi
if [[ -n "$failed" ]];then
	log "certbot failed domains: $failed" >&2
fi
if [[ -n "$updated" ]];then
	log "certbot updated domains: $updated" >&2
fi
# vim:set et sts=4 ts=4 tw=0 et: