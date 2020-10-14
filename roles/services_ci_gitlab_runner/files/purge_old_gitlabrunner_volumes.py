#!/usr/bin/env python3
import os
import sys
import datetime
from datetime import timedelta
import subprocess
import json
import logging

L = logging.getLogger('docker.purger')

B = os.path.basename
FAKE = os.environ.get('FAKE', '') == '1'
TTL = int(os.environ.get('PURGE_TTL', 60 * 60 * 24 * 31 * 3))
MAXSIZE = int(os.environ.get('MAXSIZE', 100*1024*1024))


def run(cmd, method='check_output', *args, **kwargs):
    L.info(f'Running: {cmd}')
    ret = getattr(subprocess, method)(cmd, *args, **kwargs)
    if method not in ['run']:
        ret = ret.decode('utf-8')
    return ret


def main():
    logging.basicConfig(level=logging.INFO)
    res = {'toremove': [], 'skipped': [], 'removed': []}
    if FAKE:
        cmd = 'echo 1 /var/lib/docker/volumes/c747a884eb35882ff69a5e4a544e52b66c96e2217119d613297ed543fc9ac5eb'
    else:
        cmd = f'du -shc --threshold={MAXSIZE} /var/lib/docker/volumes/*'

    t = run(cmd, stderr=subprocess.STDOUT, shell=True)

    for voldata in [a for a in t.splitlines()][:-1]:
        if not voldata.strip():
            continue
        size, location = voldata.split()
        vol = B(location)
        # must be in SHA form
        if len(vol) != 64:
            continue
        cmd = f'docker volume inspect {vol}'
        dt = json.loads(run(cmd, stderr=subprocess.STDOUT, shell=True))
        createdat = datetime.datetime.strptime(dt[0]['CreatedAt'][:-6], '%Y-%m-%dT%H:%M:%S')
        now = datetime.datetime.now()
        data = (voldata, size, location, vol, createdat)
        k = 'skipped'
        if (now - createdat).total_seconds() >= TTL:
            k = 'toremove'
        res[k].append(data)
    for (voldata, size, location, vol, createdat) in res['toremove']:
        cmd = f'docker volume rm -f {vol}'
        t = run(cmd, stderr=subprocess.STDOUT, shell=True, method='run')
        res['removed'].append((voldata, size, location, vol, createdat))


if __name__ == '__main__':
    main()
