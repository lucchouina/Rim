<?xml version="1.0" ?>
<spec version="1.0">
    <module name="osBase" version="1.0" flags="required" level="2" prime="1" fs="squashfs">
        <!-- / -->
        <element source="/firstboot" type="emptyfile" />
        <element source="/dopost" type="emptyfile" />

        <!-- bin -->
        <element source="/usr/bin/bzip2"/>
        <element source="/bin/chgrp"/>
        <element source="/bin/chown"/>
        <element source="/bin/date"/>
        <element source="/bin/domainname"/>
        <element source="/bin/echo"/>
        <element source="/bin/egrep"/>
        <element source="/bin/gunzip"/>
        <element source="/bin/kill"/>
        <element source="/bin/nano"/>
        <element source="/bin/mktemp"/>
        <element source="/bin/more"/>
        <element source="/bin/pwd"/>
        <element source="/bin/readlink" />
        <element source="/bin/sleep" />
        <element source="/bin/stty"/>
        <element source="/bin/su" perms="4755"/>
        <!--element source="/bin/tempfile"/-->
        <element source="/bin/uname"/>
        <element source="/bin/zcat"/>
        <element source="/usr/bin/run-parts"/>

        <!-- sbin -->
        <element source="/usr/sbin/ethtool"/>
        <element source="/sbin/hwclock"/>
        <element source="/sbin/ifdown"/>
        <element source="/sbin/ifup"/>
        <element source="/sbin/nologin"/>
        <element source="/sbin/runlevel"/>
        <element source="/sbin/shutdown"/>
        <element source="/sbin/swapoff"/>
        <element source="/sbin/unix_chkpwd"/>
        <element source="/sbin/start-stop-daemon"/>

        <!-- usr/bin -->
        <element source="/bin/nice"/>
        <element source="/bin/basename"/>
        <element source="/bin/sort"/>
        <element source="/bin/ipcalc"/>
        <element source="/usr/bin/clear"/>
        <element source="/usr/bin/cut"/>
        <element source="/usr/bin/diff"/>
        <element source="/usr/bin/du"/>
        <element source="/usr/bin/env"/>
        <element source="/usr/bin/file"/>
        <element source="/usr/bin/flock"/>
        <element source="/usr/share/misc/magic"/>
        <element source="/usr/bin/expr"/>
        <element source="/usr/bin/find"/>
        <element source="/usr/bin/getent"/>
        <element source="/usr/bin/getopt"/>
        <element source="/usr/bin/groups"/>
        <element source="/usr/bin/head"/>
        <element source="/usr/bin/less"/>
        <element source="less" target="/usr/bin/pager" type="link"/>
        <element source="/usr/bin/logger"/>
        <element source="/usr/bin/md5sum"/>
        <element source="/usr/bin/mkfifo"/>
        <element source="/usr/bin/od"/>
        <element source="/usr/bin/passwd"/>
        <element source="/usr/share/cracklib" type="dir" recurse="1" mask="*"/>
        <element source="/usr/bin/pgrep"/>
        <element source="/usr/bin/pkill"/>
        <element source="/usr/bin/script"/>
        <element source="/usr/bin/stat"/>
        <element source="/usr/bin/strace"/>
        <element source="/usr/bin/strings"/>
        <element source="/usr/bin/sudo" perms="04755" />
        <element source="/usr/bin/sum"/>
        <element source="/usr/bin/tail"/>
        <element source="/usr/bin/tee"/>
        <element source="/usr/bin/telnet"/>
        <element source="/usr/bin/top"/>
        <element source="/usr/bin/tput"/>
        <element source="/usr/bin/tr"/>
        <element source="/usr/bin/uniq"/>
        <element source="/usr/bin/uptime"/>
        <element source="/bin/vi"/>
        <element source="/usr/bin/vmstat"/>
        <element source="/usr/bin/w"/>
        <element source="/usr/bin/wc"/>
        <element source="/usr/bin/which"/>
        <element source="/usr/bin/whoami"/>
        
        <!-- ntp suite 
        <element source="/usr/bin/ntpdc"/>
        <element source="/usr/bin/ntpq"/>
        <element source="/usr/bin/ntpsweep"/>
        <element source="/usr/bin/ntptrace"/>
        <element source="/usr/sbin/ntp-keygen"/>
        <element source="/usr/sbin/ntp-wait"/>
        <element source="/usr/sbin/ntpd"/>
        <element source="/usr/sbin/ntpdate"/>
        <element source="/usr/sbin/ntptime"/>
        -->
        
        <!-- usr/sbin -->
        <element source="/usr/sbin/dmidecode" arch="i386 x86_64" />
        <element source="/usr/sbin/getsmbios" arch="i386 x86_64" />
        <element source="/usr/sbin/groupadd"/>
        <element source="/usr/sbin/groupdel"/>
        <element source="/usr/sbin/groupmod"/>
        <element source="/usr/sbin/iboot" arch="i386 x86_64" />
        <element source="/usr/sbin/icmd" arch="i386 x86_64" />
        <element source="/usr/sbin/iresetbmc" arch="i386 x86_64" />
        <element source="/bin/traceroute"/>
        <element source="/usr/sbin/useradd"/>
        <element source="/usr/sbin/userdel"/>
        <element source="/usr/sbin/usermod"/>
        
        <!-- sshd -->
        <element source="/usr/sbin/sshd"/>
        <element source="/usr/bin/ssh-keygen"/>
        <element source="/etc/init.d/ssh"/>
        
        <!-- firewall [ dumb down firewall support - ufw is not that uncomplicated !! ] -->
        <element source="/etc/init.d/firewall"/>
        <element source="/etc/default/ufw" type="emptyfile"/>
        <element source="/etc/firewall.conf"/>
        <element source="/sbin/firewall" target="/usr/sbin/ufw" type="link"/>
        <element source="/sbin/firewall" />
        <element source="/sbin/iptables"/>
        <element source="/lib/xtables" type="dir" recurse="1" mask="*"/>

        <!-- cron -->
        <element source="/usr/sbin/crond"/>
        <element source="/usr/sbin/atd"/>
        <element source="/usr/bin/at"/>
        <element source="/etc/sysconfig/crond"/>
        <element source="/usr/bin/crontab"/>
        <element source="/etc/cron.d" type="emptydir"/>
        <element source="/etc/crontab"/>
        <element source="/etc/wpa_supplicant/ifupdown.sh"/>
        <element source="/etc/cron.deny" type="emptyfile" />        
        <element source="/var/spool/cron" type="emptydir" />        
        <element source="/etc/init.d/atd"/>
        <element source="/etc/default/atd"/>
        <element source="/var/spool/cron/crontabs" type="emptydir" perm="0730" />
        
        <!-- etc -->
        <element source="/etc/login.defs"/>
        <element source="/etc/resolv.conf"/>
        <element source="/etc/sudoers" perms="0440"/>
        <element source="/etc/sysctl.d" type="dir" recurse="1" mask="*" />
        <element source="/etc/sudoers.d" type="emptydir" perms="0550" />
        <element source="/etc/sudoers.d/README" type="emptyfile" perms="0440" />
        <element source="/etc/ssh"          type="dir" recurse="1" mask="*"/>
        <element source="/var/lock/subsys"  type="dir" perm="0755"/>
        
        <!-- nss support libs. Rim will not find these through elf scans... -->
        <element source="/lib/libnss_dns.so.2"/>

        <!-- logrotate -->
        <element source="/usr/sbin/logrotate"/>
        <element source="/etc/cron.daily/logrotate"/>
        <element source="/etc/logrotate.conf"/>
        <element source="/etc/logrotate.d/rsyslog"/>
        <element source="/var/lib/logrotate" type="emptydir" />
        
        <!-- rsyslog -->       
        <element source="/sbin/rsyslogd"/>
        <element source="/etc/default/rsyslog"/>
        <element source="/etc/rsyslog.conf"/>
        <element source="/etc/rsyslog.d" type="dir" recurse="1" mask="*"/>
        <element source="/lib/rsyslog/imfile.so"/>
        <element source="/lib/rsyslog/imklog.so"/>
        <element source="/lib/rsyslog/immark.so"/>
        <element source="/lib/rsyslog/imtcp.so"/>
        <element source="/lib/rsyslog/imudp.so"/>
        <element source="/lib/rsyslog/imuxsock.so"/>
        <element source="/lib/rsyslog/lmnet.so"/>
        <element source="/lib/rsyslog/lmnetstrms.so"/>
        <element source="/lib/rsyslog/lmnsd_ptcp.so"/>
        <element source="/lib/rsyslog/lmregexp.so"/>
        <element source="/lib/rsyslog/lmtcpclt.so"/>
        <element source="/lib/rsyslog/lmtcpsrv.so"/>
        <element source="/lib/rsyslog/ommail.so"/>

        <!-- hwclock, procps -->
        <element source="/etc/init.d/hwclock" />
        <element source="/etc/init.d/procps"/>

        
        <!-- dmesg -->
        <element source="/etc/init.d/dmesg" />
        <element source="../init.d/dmesg" target="/etc/rc5.d/S03dmesg" type="link"/>
        
        <!-- kexec/kdump support -->
        <element source="/etc/init.d/kexec"/>
        <element source="/sbin/kexec"/>
        <element source="../init.d/kexec" target="/etc/rc5.d/S00kexec" type="link"/>
        <element source="/boot/zImage"/>        
        <element source="/bin/makedumpfile"/>        
        <element source="/etc/logrotate.d/vmcores"/>

        <!-- 
        <element source="/etc/init.d/kexec-load"/>
        <element source="../init.d/kexec-load" target="/etc/rc6.d/K18kexec-load" type="link"/>
        -->

        <element source="/etc/default/locale"/>
        <element source="/etc/environment"/>
        <element source="/usr/sbin/irqbalance" arch="i386 x86_64" />

        <!-- Watchdog -->
        <element source="/usr/sbin/watchdog" />
        <element source="/usr/sbin/wd_keepalive" />
        <element source="/usr/sbin/wd_identify" />
        <element source="/etc/sysconfig/watchdog" />
        <element source="/etc/watchdog.conf" />
        <element source="/etc/init.d/watchdog" />
        <element source="/dev/watchdog" type="node" nodetype="c" major="10" minor="130" />
                
        <!-- Shutdown/reboot processing, we need to include some sysv files -->
        <element source="/etc/init.d/reboot"/>
        <element source="/etc/init.d/halt"/>
        <element source="/etc/init.d/killprocs"/>
        <element source="/etc/init.d/single"/>
        <element source="/etc/default/halt" />

        <!-- network -->
        <element source="/etc/init.d/network"/>
        <element source="/etc/network" type="dir" recurse="1" mask="*"/>
        <element source="/etc/network/if-down.d" type="emptydir" />
        <element source="/var/run/network" type="emptydir" />
        <element source="/sbin/dhclient"/>
        <element source="/sbin/dhclient-script"/>
        <element source="/etc/dhcp/dhclient.conf"/>
                
        <!-- pam -->
        <include spec="pam.inc"/>
        
        <!-- Localization -->
        <element source="/usr/lib/locale" type="dir" recurse="1" mask="*"/>
        <element source="/usr/share/terminfo/l/linux"  />
        <element source="/usr/share/terminfo/x" type="dir" mask="xterm.*" />
        
        <!-- Openssl -->
        <element source="/usr/bin/openssl"/>
        <element source="/usr/lib/openssl" type="dir" recurse="1" mask="*"/>
        <element source="/etc/pki" type="dir" recurse="1" mask="*"/>
        
        <!-- Uuid -->
        <element source="/usr/bin/uuidgen"/>       
        <element source="/usr/sbin/uuidd"/>
        
        <!-- Acpi -->
        <element source="/etc/acpi/events/powerbtn" arch="i386 x86_64" />
        <element source="/etc/acpi/powerbtn.sh" arch="i386 x86_64" />
        <element source="/etc/init/acpid.conf" arch="i386 x86_64" />
        <element source="/etc/default/acpid" arch="i386 x86_64" />
        <element source="/usr/sbin/acpid" arch="i386 x86_64" />
        <element source="/etc/init.d/acpid" arch="i386 x86_64" />

        <script context="postinstall" rank="20">
            <![CDATA[
            
                # to make dhclient work properly
                mkdir -p /etc/rc.d
                mkdir -p /etc/ssh
                cp $rimCurRoot/etc/hostname /etc/hostname 2>/dev/null
                cp $rimCurRoot/etc/hosts /etc/hosts 2>/dev/null
                cp $rimCurRoot/etc/passwd /etc/passwd 2>/dev/null
                cp $rimCurRoot/etc/shadow /etc/shadow 2>/dev/null
                cp $rimCurRoot/etc/group /etc/group 2>/dev/null
                cp $rimCurRoot/etc/gshadow /etc/gshadow 2>/dev/null
                cp $rimCurRoot/etc/ssh/*_key /etc/ssh 2>/dev/null
                chmod 0400 /etc/ssh/*_key 2>/dev/null
                chmod 0440 /etc/sudoers.d/* 2>/dev/null
                echo $rim_node > /etc/hostname
                /bin/hostname -b -F /etc/hostname
                grep -q $rim_node /etc/hosts || echo "127.0.0.1 $rim_node" >> /etc/hosts
                echo $rimBuildLabel > /etc/${rimNode}-${rimApplication}-${rimProduct}-release 2>/dev/null
                #
                # Always perform these operations on the rw jail
                #
                mkdir -p /var/run
                touch /var/run/utmpx
                ln -s /tmp /var/tmp
                mkdir -p /var/log
                mkdir -p /var/empty/sshd
                mkdir -p /var/lib
                mkdir -p /var/evlog
                mkdir -p /var/spool/cron
                mkdir -p /var/spool/at
                mkdir -p /var/lock/subsys
                mkdir -p /var/run/netreport
                #
                # some utilities will not be happy and will emit formal complains
                # about the modules dependencies file not being there.
                # Create one...
                #
                mkdir /lib/modules/`uname -r`
                touch /lib/modules/`uname -r`/modules.dep
                #
                # at support
                #
                mkdir /var/spool/cron/atjobs
                mkdir /var/spool/cron/atspool
                touch /var/spool/cron/atjobs/.SEQ
                chown -R daemon /var/spool/cron/atjobs /var/spool/cron/atspool
                return 0
             ]]>
        </script>
        <script context="up" rank="20">
            <![CDATA[
                touch /var/run/utmpx
                return 0
             ]]>
        </script>
        <script context="firstbootpredb" rank="10">
            <![CDATA[
             ]]>
        </script>
        <script context="firstboot" rank="10">
            <![CDATA[
             ]]>
        </script>
    </module>
</spec>
        
