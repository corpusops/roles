# {{ ansible_managed }}
# {% set  default_tz = corpusops_localsettings_timezone_vars.timezone %}
export TZ="{{default_tz}}"
# redhat
export ZONE="{{default_tz}}"
