<?xml version="1.0" ?>
<spec version="1.0">
    <module name="osBase" version="1.0" flags="required" level="2" prime="1" fs="squashfs">
        <!-- / -->
        <element source="/firstboot"/>

        <!-- bin -->
        <element source="/bin/basename"/>
        <element source="/bin/chown"/>
        <element source="/bin/chgrp"/>
        <element source="/bin/date"/>
        <element source="/bin/egrep"/>
        <element source="/bin/hostname"/>
        <element source="/bin/ipcalc"/>
        <element source="/bin/kill"/>
        <element source="/bin/nice"/>

        <!-- no of our cronjobs assume /usr/bin/nice ... -->
        <element source="../../bin/nice"  target="/usr/bin/nice" type="link"/>
        <element source="/bin/pwd"/>
        <element source="/bin/sleep" />
        <element source="/bin/sort"/>
        <element source="/bin/stty"/>
        <element source="/bin/su" perms="4755"/>
        <element source="/bin/touch"/>
        <element source="/bin/uname"/>
        <element source="/bin/usleep"/>
        <element source="/bin/traceroute"/>
        <element source="/bin/zcat"/>

        <!-- sbin -->
        <element source="/sbin/ethtool"/>
        <element source="/sbin/evlactiond"/>
        <element source="/sbin/evlogmgr"/>
        <element source="/sbin/evlnotifyd"/>
        <element source="/sbin/evlogd"/>
        <element source="/sbin/hwclock"/>
        <element source="/sbin/ifdown"/>
        <element source="/sbin/ifup"/>
        <element source="/sbin/kexec"/>
        <element source="/sbin/runlevel"/>
        <element source="/sbin/shutdown"/>
        <element source="/sbin/syslog-ng"/>
        <element source="/sbin/udevd"/>
        <element source="/sbin/unix_chkpwd"/>
        <element source="/sbin/swapon"/>
        <element source="/sbin/swapoff"/>

        <!-- usr/bin -->
        <element source="/usr/bin/bzip2"/>
        <element source="/usr/bin/clear"/>
        <element source="/usr/bin/cut"/>
        <element source="/usr/bin/diff"/>
        <element source="/usr/bin/du"/>
        <element source="/usr/bin/file"/>
        <element source="/usr/bin/find"/>
        <element source="/usr/bin/gunzip"/>
        <element source="/usr/bin/head"/>
        <element source="/usr/bin/less"/>
        <element source="/usr/bin/logger"/>
        <element source="/usr/bin/mktemp"/>
        <element source="/usr/bin/nc"/>
        <element source="/usr/bin/od"/>
        <element source="/usr/bin/passwd"/>
        <element source="/usr/bin/pgrep"/>
        <element source="/usr/bin/pkill"/>
        <element source="/usr/bin/run-parts"/>
        <element source="/usr/bin/script"/>
        <element source="/usr/bin/ssh-keygen"/>
        <element source="/usr/bin/stat"/>
        <element source="/usr/bin/strace"/>
        <element source="/usr/bin/strings"/>
        <element source="/usr/bin/sudo"/>
        <element source="/usr/bin/sum"/>
        <element source="/usr/bin/tail"/>
        <element source="/usr/bin/tee"/>
        <element source="/usr/bin/telnet"/>
        <element source="/usr/bin/top"/>
        <element source="/usr/bin/tr"/>
        <element source="/usr/bin/uniq"/>
        <element source="/usr/bin/uptime"/>
        <element source="/bin/vi"/>
        <element source="/usr/bin/vmstat"/>
        <element source="/usr/bin/w"/>
        <element source="/usr/bin/wc"/>
        <element source="/usr/bin/which"/>
        <element source="/usr/bin/whoami"/>
        <element source="/usr/bin/xxd"/>

        <!-- usr/sbin -->
        <element source="/usr/sbin/acpid"/>
        <element source="/usr/sbin/crond"/>
        <element source="/usr/sbin/getsmbios"/>
        <element source="/usr/sbin/groupadd"/>
        <element source="/usr/sbin/groupdel"/>
        <element source="/usr/sbin/groupmod"/>
        <element source="/usr/sbin/iboot"/>
        <element source="/usr/sbin/icmd"/>
        <element source="/usr/sbin/iresetbmc"/>
        <element source="/usr/sbin/logrotate"/>
        <element source="/usr/sbin/ntpdate"/>
        <element source="/usr/sbin/rngd"/>
        <element source="/usr/sbin/sshd"/>
        <element source="/usr/sbin/tamutil"/>
        <element source="/usr/sbin/useradd"/>
        <element source="/usr/sbin/userdel"/>
        <element source="/usr/sbin/usermod"/>
        <element source="/usr/sbin/watchdog"/>

         <!-- etc -->
        <element source="/etc/crontab"/>
        <element source="/etc/login.defs"/>
        <element source="/etc/logrotate.conf"/>
        <element source="/etc/resolv.conf"/>
        <element source="/etc/sudoers" perms="0440"/>
        <element source="/etc/syslog-ng/syslog-ng.conf"/>
        <element source="/etc/sysconfig/syslog-ng"/>
        <element source="/etc/sysconfig/network-scripts/ifcfg-lo"/>
        <element source="/etc/sysconfig/network-scripts/ifup-ipv6"/>
        <element source="/etc/sysconfig/network-scripts/ifup-post"/>
        <element source="/etc/sysconfig/network-scripts/ifup-eth"/>
        <element source="/etc/sysconfig/network-scripts/ifup-aliases"/>
        <element source="/etc/sysconfig/network-scripts/ifup-routes"/>
        <element source="/etc/sysconfig/network-scripts/ifdown-ipv6"/>
        <element source="/etc/sysconfig/network-scripts/ifdown-post"/>
        <element source="/etc/sysconfig/network-scripts/ifdown-eth"/>
        <element source="/etc/sysconfig/network-scripts/ifdown-routes"/>
        <element source="/etc/sysconfig/network-scripts/network-functions"/>
        <element source="/etc/sysconfig/udev"/>
        <element source="/etc/watchdog.conf"/>
        <element source="/etc/cron.d"       type="dir" recurse="1" mask="*"/>
        <element source="/etc/cron.daily"   type="dir" recurse="1" mask="*"/>
        <element source="/etc/logrotate.d"  type="dir" recurse="1" mask="*"/>
        <element source="/etc/rc.d"         type="dir" recurse="1" mask="*"/>
        <element source="/etc/ssh"          type="dir" recurse="1" shadow="1" mask="*"/>
        <element source="/etc/watchdog_test_binary.pl"   perms="4755"/>   
        
        
        <element source="/lib/modules"      type="dir" recurse="1" mask="*"/>
        <element source="/var/lock/subsys"  type="dir" perm="0755"/>
        
        <element source="rc.d/init.d"      target="/etc/init.d" type="link"/>
        <element source="rc.d/rc0.d"       target="/etc/rc0.d"  type="link"/>
        <element source="rc.d/rc1.d"       target="/etc/rc1.d"  type="link"/>
        <element source="rc.d/rc3.d"       target="/etc/rc3.d"  type="link"/>
        <element source="rc.d/rc6.d"       target="/etc/rc6.d"  type="link"/>

        <include spec="pam.inc"/>
        <element source="/usr/share/cracklib" type="dir" recurse="1" mask="*"/>

        <!-- drivers, their scripts and their libs -->
        <!--include spec="//$BLDROOT/lp/smlc-l/tptran/wrl_30/tptran.spec"/ ### removed for CAS - should be moved into SMLC, anyway ###-->
        <!--element source="lib/modules/2.6.27/kernel/drivers/net/kgdboe.ko" target="/tpapp/tptran/drivers/kgdboe.ko" perms="0755"/-->
        <!--element source="lib/modules/2.6.27/kernel/net/tipc/tipc.ko" target="/tpapp/tptran/drivers/tipc.ko" perms="0755"/-->
        <!--element source="lib/modules/2.6.27/kernel/drivers/net/bonding/bonding.ko" target="/tpapp/tptran/drivers/bonding.ko" perms="0755"/-->
        <!--element source="lib/modules/2.6.27/kernel/drivers/serial/8250_kgdb.ko" target="/tpapp/tptran/drivers/8250_kgdb.ko" perms="0755"/-->
        <element source="lib/modules/2.6.27.39/modules.dep"/>
        
        <!-- boot -->
        <element source="/boot" type="dir" recurse="1" mask="*"/>
        
        <!-- /usr/lib  - some basic libraries that are always needed and might not be caught
             if the target we end up constructing reference them FIXME - need to add certain
             libs on the fly based on Programs dependencies and types (scons internals...)
        -->
        <element source="/usr/lib/libstdc++.so.6"/>
        <element source="libstdc++.so.6" target="/usr/lib/libstdc++.so" type="link"/>
        
    </module>
</spec>
        
