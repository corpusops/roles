#!/usr/bin/env bash
#{%- set u = corpusops_localsettings_jdk_vars.urls %}
#{%- set v = u.get("{version}-{flavor}".format(**corpusops_localsettings_jdk_vars), {}) %}
#{% if v %}
#{%- else %}
#{%- set v = { 'd': '/usr/lib/jvm/java-{version}-oracle'.format( **corpusops_localsettings_jdk_vars)} %}
#{%- endif %}
#{% if v %}

export J2SDKDIR={{v.d}}
export J2REDIR={{v.d}}/jre
export JAVA_HOME={{v.d}}
export DERBY_HOME={{v.d}}/db
export PATH=${JAVA_HOME}/bin:${DERBY_HOME}/bin:${JRE_HOME}/bin:${PATH}
#-{% endif %}
# vim:set et sts=4 ts=4 tw=80:
