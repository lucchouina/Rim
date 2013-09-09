#!/bin/bash
exec 2>/tmp/setSysConfig.out 1>&2

#
# handler 'System'
#
telinit 5


#
# notification 'IPInfo'
#
service rc4 restart


#
# handler 'TimeInfo'
#
service rc5 restart

#
# handler 'IPInfo'
#
restart rc2

