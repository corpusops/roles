#!/usr/bin/env bash
#{%- set u = corpusops_localsettings_golang_vars.urls %}
#{%- set v = u.get("{version}-{flavor}".format(**corpusops_localsettings_golang_vars), {}) %}
#{% if v %}
#{%- else %}
#{%- set v = { 'd': '/usr/lib/jvm/java-{version}-oracle'.format( **corpusops_localsettings_golang_vars)} %}
#{%- endif %}
#{% if v %}

setenv GOROOT {{v.d}}/go
export PATH ${GOROOT}/bin:${PATH}
#-{% endif %}
# vim:set et sts=4 ts=4 tw=80:
