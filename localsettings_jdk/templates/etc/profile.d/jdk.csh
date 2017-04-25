#!/usr/bin/env bash
#{%- set u = corpusops_localsettings_jdk_vars.urls %}
#{%- set v = u.get("{version}-{flavor}".format(**corpusops_localsettings_jdk_vars), {}) %}
#{% if v %}
#{%- else %}
#{%- set v = { 'd': '/usr/lib/jvm/java-{version}-oracle'.format( **corpusops_localsettings_jdk_vars)} %}
#{%- endif %}
#{% if v %}

setenv J2SDKDIR {{v.d}}
setenv J2REDIR {{v.d}}/jre
setenv JAVA_HOME {{v.d}}
setenv DERBY_HOME {{v.d}}/db
setenv PATH ${JAVA_HOME}/bin:${DERBY_HOME}/bin:${JRE_HOME}/bin:${PATH}
#-{% endif %}
# vim:set et sts=4 ts=4 tw=80:
