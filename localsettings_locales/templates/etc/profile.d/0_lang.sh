# {{ ansible_managed }}
# {% set  default_locale = corpusops_localsettings_locales_vars.locale %}
export LANG="{{ default_locale }}"
export LC_CTYPE="{{ default_locale }}"
export LC_NUMERIC="{{ default_locale }}"
export LC_TIME="{{ default_locale }}"
export LC_COLLATE="{{ default_locale }}"
export LC_MONETARY="{{ default_locale }}"
export LC_MESSAGES="{{ default_locale }}"
export LC_PAPER="{{ default_locale }}"
export LC_NAME="{{ default_locale }}"
export LC_ADDRESS="{{ default_locale }}"
export LC_TELEPHONE="{{ default_locale }}"
export LC_MEASUREMENT="{{ default_locale }}"
export LC_IDENTIFICATION="{{ default_locale }}"
export LC_ALL=""
