#!/usr/bin/env bash
# {{ ansible_managed}}
exec pg-wrapper-{{corpusops_services_db_postgresql_version}}.sh \
    {{item}} $@
