#!/bin/bash
cd $(dirname $(readlink -f $0))/files
curl https://raw.githubusercontent.com/Napsty/check_smart/master/check_smart.pl >  check_smart.pl
chmod +x check*
