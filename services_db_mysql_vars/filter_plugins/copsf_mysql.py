#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import six


def setupdefault(data, var, value):
    if data.get(var, None) is None:
        data[var] = value
    return value


def copsf_mysql(data, ansible_vars, prefix):
    # update defaults from the selected mode (default|prod)
    # only if any value is not explicitly set by the user
    defaults = data['modes'].get(data['mode'],
                                 data['modes']['default'])
    for i, val in six.iteritems(defaults):
        setupdefault(data, i, val)
    # Now let's do the autotuning magic:
    # Some heavy memory usage settings could be used on mysql settings:
    # Below are the rules we use to compute some default magic
    # values for tuning settings.
    # Note that you can enforce any of theses settings by putting
    # some value fro them in
    # mysqlSettings (so in the pillar for example).
    # The most important setting for this tuning is the amount of the
    # total memory you
    # allow for MySQL, given by the % of total memory set in
    # mysqlSettings.memory_usage_percent
    # So starting from total memory * given percentage we use
    # (let's call it available memory):
    # * innodb_buffer_pool_size: 50% of avail.
    # * key_buffer_size:
    # * query_cache_size: 20% of avail. limit to 500M as a starting point
    # # -- per connections
    # * max_connections -> impacts on per conn memory settings
    #   (which are big)
    # and number of tables and files opened
    # * innodb_log_buffer_size:
    # * thread_stack
    # * thread_cache_size
    # * sort_buffer_size
    # # -- others
    #  * tmp_table_size == max_heap_table_size : If working data memory for
    #    a request
    #               gets bigger than that then file backed temproray tables
    #               will be used(and it will, by definition, be big ones),
    #               the bigger the better but you'll need RAM, again.
    # * table_open_cache
    # * table_definition_cache
    # first get the Mo of memory, cpu and disks on the system
    full_mem = setupdefault(
        data, 'full_mem',
        ansible_vars['ansible_memtotal_mb'])
    nb_cpus = setupdefault(
        data, 'nb_cpus',
        ansible_vars['ansible_processor_cores'])
    # Then extract memory that we could use for this MySQL server
    available_mem = setupdefault(
        data, 'available_mem',
        full_mem * data['memory_usage_percent'] / 100)
    available_mem = data['available_mem']
    # Now for all non set tuning parameters try to fill the gaps
    # ---- NUMBER OF CONNECTIONS
    # ---- QUERY CACHE SIZE
    try:
        query_cache_size_M = int((available_mem / 5))
    except (ValueError, TypeError):
        query_cache_size_M = 500
        if query_cache_size_M > 500:
            query_cache_size_M = 500
    query_cache_size_M = setupdefault(
        data, 'query_cache_size_M', query_cache_size_M)
    # ---- INNODB BUFFER
    # Values cannot be used in default/context
    # as others as we need to compute from previous values
    innodb_buffer_pool_size_M = setupdefault(
        data, 'innodb_buffer_pool_size_M', int((available_mem / 2)))
    # Try to divide this buffer in instances of 1Go
    innodb_buffer_pool_instances = setupdefault(
        data, 'innodb_buffer_pool_instances',
        int(round((innodb_buffer_pool_size_M / 1024), 0)))
    if innodb_buffer_pool_instances < 1:
        innodb_buffer_pool_instances = 1
    data['innodb_buffer_pool_instances'] = innodb_buffer_pool_instances

    # Try to set this to 25% of innodb_buffer_pool_size
    setupdefault(data, 'innodb_log_buffer_size_M',
                 int(round((innodb_buffer_pool_size_M / 4), 0)))

    # ------- INNODB other settings
    setupdefault(data, 'innodb_flush_method', 'O_DSYNC')
    # recommended value is 2*nb cpu + nb of disks, we assume one disk
    setupdefault(data, 'innodb_thread_concurrency',
                 int(nb_cpus + 1) * 2)
    # Should we sync binary logs at each commits or prey
    # for no server outage?
    setupdefault(data, 'sync_binlog', 0)
    # innodb_flush_log_at_trx_commit
    #  1 = Full ACID, but slow, log written at commit + sync disk
    #  0 = log written every second + sync disk,
    #      BUT nothing at commit (kill of mysql can loose
    #      last transactions)
    #  2 = log written every second + sync disk,
    #      and log written at commit without sync disk
    #      (server outage can loose transactions)
    #
    # --------- Settings related to number of tables
    # This is by default 8M, should store all tables and indexes
    setupdefault(data, 'innodb_flush_log_at_trx_commit', 1)
    if data['number_of_table_indicator'] < 251:
        innodb_additional_mem_pool_size_M = 8
    elif data['number_of_table_indicator'] < 501:
        innodb_additional_mem_pool_size_M = 16
    elif data['number_of_table_indicator'] < 1001:
        innodb_additional_mem_pool_size_M = 24
    else:
        innodb_additional_mem_pool_size_M = 32
    innodb_additional_mem_pool_size_M = setupdefault(
        data, 'innodb_additional_mem_pool_size_M',
        innodb_additional_mem_pool_size_M)
    # TABLE CACHE
    #  table_open_cache should be
    #           max joined tables in queries * nb connections
    #  table_cache is the old name now
    #       it's table_open_cache and by default 400
    #  the system open_file_limit may not be good enough
    #  If server crash try to tweak "sysctl fs.file-max"
    #  or check mysql ulimit
    #  Warning /etc/security/limits.conf is not read
    #  by upstart (it's for users)
    #  so the increase of file limits must be set in upstart script
    #  http://askubuntu.com/questions/288471/mysql-cant-open-files-after-updating-server-errno-24
    setupdefault(data, 'table_definition_cache',
                 data['number_of_table_indicator'])
    table_open_cache = setupdefault(data, 'table_open_cache',
                                    data['nb_connections'] * 8)
    # this should be table_open_cache * nb_connections
    setupdefault(data, 'open_file_limit',
                 data['nb_connections'] * table_open_cache)
    # tmp_table_size: On queries using temporary data, is this data gets
    # bigger than then the temporary memory things becames real physical
    # temporary tablesand things gets very slow, but this must be some free
    # RAM when the request is running, so if you use something like
    # 1024Mo prey that queries using this amount
    # of temporary data are not running too often...
    setupdefault(data, 'tmp_table_size_M',
                 int((data['available_mem'] / 10)))
    data['client_packages'].extend(data['py_packages'])
    return data, ansible_vars


__funcs__ = {
    'copsf_mysql': copsf_mysql,
}


class FilterModule(object):

    def filters(self):
        return __funcs__
# vim:set et sts=4 ts=4 tw=80
