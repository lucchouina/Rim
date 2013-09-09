#!/usr/bin/perl -w
use strict;

#
# watchdog.conf uses this script
# test-binary = /etc/watchdog_test_binary.pl
#
# watchdog_test_binary.pl calls /etc/watchdog_test_binary_app.pl if exists. 
# watchdog_test_binary_app.pl should return 0 exit code otherwise watchdog daemon 
# reboots the system. Application RPMs (SMLC or LMUSIM) may implement the
# test-binary routine and link it to /etc/watchdog_test_binary_app.pl.
# watchdog_test_binary_app.pl should exit with code 0 before watchdog calls it again.
#
# EXIT STATUS: This script should return 0 exit code otherwise watchdog daemon 
#              reboots the system

#
# always kick the ipmi watchdog
# if there is a failure - we won't run 
system("ipmiutil wdt -r");
if ( -x "/etc/watchdog_test_binary_app.pl" )
{ 
  system("killall -KILL watchdog_test_binary_app.pl > /dev/null 2>&1");
  system("/etc/watchdog_test_binary_app.pl > /dev/null 2>&1");
  exit $?;
}
else
{ 
  exit 0;
}

