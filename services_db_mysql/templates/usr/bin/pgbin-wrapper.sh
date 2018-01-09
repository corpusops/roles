#!/usr/bin/env bash
# {{ ansible_managed}}
exec mysql-wrapper-{{corpusops_services_db_mysql_version}}.sh \
    {{item}} $@
