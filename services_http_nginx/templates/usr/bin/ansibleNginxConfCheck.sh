#!/bin/bash
# {{ansible_managed}}
echo "{"
/usr/sbin/nginx -t 2>&1 |grep -q "test is successful"
if [[ "$?" = "0" ]]; then
    EXIT=0
else
    /usr/sbin/nginx -t 2>&1
    EXIT=1
fi
exit $EXIT
