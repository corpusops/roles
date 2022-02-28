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
CERTBOT="${CERTBOT:-$(get_command certbot)}"
for i in bc openssl $CERTBOT;do
    if ! ( has_command $i; );then
        log "Missing; $i"
        log "Install prereqs: dnsutils or iproute2 bc openssl"
        exit 1
    fi
done
chrono=$(date "+%F-%T")
failed=""
EXPIRY={{d.expiry}}
exp_limit={{d.days}}
CERTBOT_CONFIGDIR="${CERTBOT_CONFIGDIR:-{{d.configdir}}}"
CERTBOT_WORKDIR="${CERTBOT_WORKDIR:-{{d.workdir}}}"
CONFIG="${CERTBOT_CONFIG:-{{d.dns_config}}}"
PREFERED_CHALLENGES="{{d.preferred_challenges|join(' ')}}"
DEFAULT_CERTBOT_DOMAINS="{{d.dns_domains|join('\n')}}"
CERTBOT_DOMAINS="${CERTBOT_DOMAINS:-$DEFAULT_CERTBOT_DOMAINS}"
updated=""
cli_args="{{d.dns_certonly_args.replace('\n', '')}}"
if [[ -n "$CERTBOT_DOMAINS" ]];then
exitcode=0
do_challenge() {
    if ( echo "$domain" | egrep -q "^*." );then
        $CERTBOT certonly $force_args $cli_args --preferred-challenges $i -d "$domain" -d "*.$domain"
    else
        $CERTBOT certonly $force_args $cli_args --preferred-challenges $i -d "$domain"
    fi

}
while read domain;do
if [[ -n $domain ]];then
    domain_args="-d $domain"
    if ( echo "$domain" | egrep -q "^*." );then
        domain="${domain:2}"
    fi
	cert_file="$CERTBOT_CONFIGDIR/live/$domain/fullchain.pem"
	key_file="$CERTBOT_CONFIGDIR/live/$domain/privkey.pem"
	force="${FORCE_RENEW-}"
	# check if exposed public ip is tied to the requested domain
    force_args="${FORCE_ARGS-}"
    # force_args="--force-renewal"
	if [ ! -f "$cert_file" ]; then
		log "certificate file not found for domain $domain." >&2
		force=1
	else
		exp=$(date -d "$(openssl x509 -in $cert_file -text -noout\
			|grep "Not After"|cut -c 25-)" +%s)
		datenow=$(date -d "now" +%s)
		days_exp=$(echo \( $exp - $datenow \) / $EXPIRY |bc)
	fi
    if [ "x${force}" = "x" ] && [ $days_exp -gt $exp_limit ] ; then
		msg="The certificate for $domain is up to date,"
        msg="$msg no need for renewal ($days_exp days left)."
        log $msg
	else
        echo "Starting Let's Encrypt renewal script for $domain..."
        if [ -e "$CERTBOT_CONFIGDIR/archive/${domain}" ];then
            bck="$CERTBOT_CONFIGDIR/backups/$chrono/$domain.tbz2"
            if [ ! -e "$(dirname "$bck")" ];then
                mkdir -p "$(dirname "$bck")"
            fi
            tar cjvf "$bck" \
                $(find "$CERTBOT_CONFIGDIR/"{live,renewal,archive}/{${domain},${domain}.conf} -maxdepth 0 -mindepth 0) &&\
            rm -rvf "$CERTBOT_CONFIGDIR/"{live,renewal,archive}/{${domain},${domain}.conf}
        fi
        current_updated=
        for i in $PREFERED_CHALLENGES;do
            if ( do_challenge; );then
                current_updated=1
                updated="$updated $domain"
                break
            else
                echo "Challenge $i failed for $domain" >&2
            fi
        done
        if [[ -z "$current_updated" ]];then
            failed="$failed $domain"
            exitcode=1
        fi
	fi
fi
done <<< "$CERTBOT_DOMAINS"
fi
if [[ -n "$failed" ]];then
	log "certbot failed domains: $failed"
fi
if [[ -n "$updated" ]];then
	log "certbot updated domains: $updated"
fi
exit $exitcode
# vim:set et sts=4 ts=4 tw=0 et:
