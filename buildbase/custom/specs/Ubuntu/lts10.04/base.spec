<?xml version="1.0" ?>
<spec version="1.0">
    <module name="osBase" version="1.0" flags="required" level="2" prime="1" fs="squashfs">
        <!-- / -->
        <element source="/firstboot" type="emptyfile" />
        <element source="/dopost" type="emptyfile" />
        <element source="/etc/initmode" type="emptyfile" />

        <!-- Default to False for discovery for 1.0 
        <element source="/etc/bonjour" type="emptyfile" />
        -->
        
        <!-- bin -->
        <element source="/bin/bzip2"/>
        <element source="/bin/chgrp"/>
        <element source="/bin/chown"/>
        <element source="/bin/date"/>
        <element source="/bin/echo"/>
        <element source="/bin/egrep"/>
        <element source="/bin/gunzip"/>
        <element source="/bin/domainname"/>
        <element source="/bin/kill"/>
        <element source="/bin/nano"/>
        <element source="/bin/mktemp"/>
        <element source="/bin/more"/>
        <element source="/bin/pwd"/>
        <element source="/bin/readlink"/>
        <element source="/bin/rmdir" />
        <element source="/bin/sleep" />
        <element source="/bin/stty"/>
        <element source="/bin/su" perms="4755"/>
        <element source="/bin/tempfile"/>
        <element source="/bin/uname"/>
        <element source="/bin/zcat"/>
        <element source="/bin/run-parts"/>

        <!-- sbin -->
        <element source="/usr/sbin/ethtool" version="lts10.04"/>
        <element source="/sbin/ethtool" version="lts12.04"/>
        <!--element source="/sbin/insserv"/-->
        <element source="/sbin/ifdown"/>
        <element source="/sbin/ifup"/>
        <element source="/sbin/rimRevert"/>
        <element source="/sbin/rimReset"/>
        <element source="/sbin/rimDoReset"/>
        <element source="/sbin/runlevel"/>
        <element source="/sbin/shutdown"/>
        <element source="/sbin/swapoff"/>
        <element source="/sbin/unix_chkpwd"/>
        
        <!-- usr/bin -->
        <element source="/usr/bin/nice"/>
        <element source="/usr/bin/basename"/>
        <element source="/usr/bin/sort"/>
        <element source="/usr/bin/ipcalc"/>
        <element source="/usr/bin/clear"/>
        <element source="/usr/bin/cut"/>
        <element source="/usr/bin/diff"/>
        <element source="/usr/bin/du"/>
        <element source="/usr/bin/env"/>
        <element source="/usr/bin/file"/>
        <element source="/usr/bin/flock"/>
        <element source="/usr/share/misc/magic" type="dir" recurse="1" mask="*" version="lts12.04"/>
        <element source="/usr/share/misc/magic.mgc" version="lts12.04"/>
        <element source="/usr/share/misc/magic" version="lts10.04"/>
        <element source="/usr/bin/expr"/>
        <element source="/usr/bin/find"/>
        <element source="/usr/bin/getent"/>
        <element source="/usr/bin/groups"/>
        <element source="/usr/bin/head"/>
        <element source="/usr/bin/less"/>
        <element source="less" target="/usr/bin/pager" type="link"/>
        <element source="/usr/bin/locale"/>
        <element source="/usr/bin/logger"/>
        <element source="/usr/bin/md5sum"/>
        <element source="/usr/bin/mkfifo"/>
        <element source="/usr/bin/nc"/>
        <element source="/usr/bin/nohup"/>
        <element source="/usr/bin/netmask"/>
        <element source="/usr/bin/od"/>
        <element source="/usr/bin/passwd"/>
        <element source="/usr/bin/pgrep"/>
        <element source="/usr/bin/pkill"/>
        <element source="/usr/bin/rsync"/>
        <element source="/usr/bin/script"/>
        <element source="/usr/bin/ssh-keygen"/>
        <element source="/usr/bin/stat"/>
        <element source="/usr/bin/strace"/>
        <element source="/usr/bin/strings"/> 
        
        <element source="/usr/bin/sudo" perms="04755" />
        <element source="/usr/lib/sudo" type="dir" recurse="1" mask="*" version="lts12.04" /> 
        
        <element source="/usr/bin/sum"/>
        <element source="/usr/bin/tail"/>
        <element source="/usr/bin/tee"/>
        <element source="/usr/bin/telnet"/>
        <element source="/usr/bin/test"/>
        <element source="/usr/bin/top"/>
        <element source="/usr/bin/tput"/>
        <element source="/usr/bin/tr"/>
        <element source="/usr/bin/uniq"/>
        <element source="/usr/bin/uptime"/>
        <element source="/usr/bin/vi"/>
        <element source="/usr/bin/vmstat"/>
        <element source="/usr/bin/w"/>
        <element source="/usr/bin/wc"/>
        <element source="/usr/bin/which"/>
        <element source="/usr/bin/whoami"/>
        <element source="/usr/bin/xxd"/>
        
        <!-- ntp suite -->
        <element source="/usr/bin/ntpdc"/>
        <element source="/usr/bin/ntpq"/>
        <element source="/usr/bin/ntpsweep"/>
        <element source="/usr/bin/ntptrace"/>
        <element source="/usr/sbin/ntp-keygen"/>
        <element source="/usr/sbin/ntp-wait"/>
        <element source="/usr/sbin/ntpd"/>
        <element source="/usr/sbin/ntpdate"/>
        <element source="/usr/sbin/ntptime"/>
    	<var name="ntpUid"       value="117" />
    	<var name="ntpGid"       value="123" />
	
        
        <!-- usr/sbin -->
        <element source="/usr/sbin/dmidecode" arch="i386 x86_64" />
        <element source="/usr/sbin/getsmbios" arch="i386 x86_64" />
        <element source="/usr/sbin/groupadd"/>
        <element source="/usr/sbin/groupdel"/>
        <element source="/usr/sbin/groupmod"/>
        <element source="/usr/sbin/iboot"/>
        <element source="/usr/sbin/icmd"/>
        <element source="/usr/sbin/invoke-rc.d"/>
        <element source="/usr/sbin/iresetbmc"/>
        <element source="/usr/sbin/sshd"/>
        <element source="/usr/sbin/traceroute"/>
        <element source="/usr/sbin/update-rc.d"/>
        <element source="/usr/sbin/useradd"/>
        <element source="/usr/sbin/userdel"/>
        <element source="/usr/sbin/usermod"/>
        
        <!-- authbind -->
        <element source="/usr/bin/authbind"/>  
        <element source="/usr/lib/authbind/libauthbind.so.1.0" target="/usr/lib/authbind/libauthbind.so.1"/>
        <element source="/usr/lib/authbind/helper"/>
        <element source="/etc/authbind/byport" type="emptydir"/>
        <element source="/etc/authbind/byaddr" type="emptydir"/>
        <element source="/etc/authbind/byuid" type="emptydir"/>

        <!-- cron -->
        <element source="/usr/sbin/cron"/>
        <element source="/usr/sbin/atd"/>
        <element source="/usr/bin/at"/>
        <element source="/usr/bin/batch"/>
        <element source="at" target="/usr/bin/atq" type="link"/>
        <element source="at" target="/usr/bin/atrm" type="link"/>
        <element source="/usr/bin/crontab"/>
        <element source="/etc/cron.d" type="emptydir"/>
        <element source="/etc/crontab"/>
        <element source="/etc/wpa_supplicant/ifupdown.sh"/>
        <element source="/etc/cron.deny" type="emptyfile" />
        <element source="/var/spool/cron/crontabs" type="emptydir" perm="0730" />
        <element source="/etc/init.d/atd"/>
        <element source="/etc/default/atd"/>
        
        <!-- RTC -->
        <element source="/etc/init.d/hwclock" />
        <element source="/sbin/hwclock"/>

        <!-- etc -->
        <element source="/etc/domainname"/>
        <element source="/etc/login.defs"/>
        <element source="/etc/resolv.conf"/>
        <element source="/etc/sudoers" perms="0440"/>
        <element source="/etc/sudoers.d" type="emptydir" perms="0550" />
        <element source="/etc/sudoers.d/README" type="emptyfile" perms="0440" />
        <element source="/etc/init.d/ssh"/>
        <element source="/etc/ssh"          type="dir" recurse="1" mask="*"/>
        <element source="/var/lock/subsys"  type="dir" perm="0755"/>
        
        <!-- nss support libs. Rim will not find these through elf scans... -->
        <element source="/lib/libnss_dns.so.2" version="lts10.04"/>
        <element source="/lib/libnss_mdns4.so.2" />
        <element source="/lib/libnss_mdns4_minimal.so.2"/>
        <element source="/lib/x86_64-linux-gnu/libnss_dns.so.2" version="lts12.04"/>
        <element source="/var/lib/ntp" type="emptydir" owner="${ntpUid}" />
        <element source="/etc/ntp.conf" />
        <element source="/etc/default/ntp" />

        <!-- rsyslog and logrotate -->
        <element source="/etc/cron.daily/logrotate"/>
        <element source="/etc/default/rsyslog"/>
        <element source="/etc/init/rsyslog.conf"/>
        <element source="/etc/logcheck/ignore.d.server/rsyslog"/>
        <element source="/etc/logrotate.conf"/>
        <element source="/etc/logrotate.d/rsyslog"/>
        <element source="/etc/rsyslog.conf"/>
        <element source="/etc/rsyslog.d" type="dir" recurse="1" mask="*"/>
        <element source="/usr/bin/savelog"/>
        <element source="/usr/lib/rsyslog/imfile.so"/>
        <element source="/usr/lib/rsyslog/imklog.so"/>
        <element source="/usr/lib/rsyslog/immark.so"/>
        <element source="/usr/lib/rsyslog/imtcp.so"/>
        <element source="/usr/lib/rsyslog/imudp.so"/>
        <element source="/usr/lib/rsyslog/imuxsock.so"/>
        <element source="/usr/lib/rsyslog/lmnet.so"/>
        <element source="/usr/lib/rsyslog/lmnetstrms.so"/>
        <element source="/usr/lib/rsyslog/lmnsd_ptcp.so"/>
        <element source="/usr/lib/rsyslog/lmregexp.so"/>
        <element source="/usr/lib/rsyslog/lmtcpclt.so"/>
        <element source="/usr/lib/rsyslog/lmtcpsrv.so"/>
        <element source="/usr/lib/rsyslog/ommail.so"/>
        <element source="/usr/sbin/logrotate"/>
        <element source="/usr/sbin/rsyslogd"/>
        <element source="/var/lib/logrotate" type="emptydir" />

        <element source="/usr/bin/install"/>
                
        <!-- Shutdown/reboot processing, we need to include some sysv files -->
        <element source="/etc/init.d/reboot"/>
        <element source="/etc/init.d/halt"/>
        <element source="/etc/default/halt" />

        <element source="/etc/init.d/network"/>
        
        <!-- sysctl config kernel push - /etc/sysctl.conf and /etc/sysctl.d/* -->
        <element source="/etc/init.d/procps"/>

        <!-- Single user mode processing, we need to include some sysv files -->
        <element source="/etc/init.d/ntp"/>
        <element source="/etc/init.d/killprocs"/>
        
        <!-- base final goals for each run level -->
        <element source="/etc/init.d/final1"/>
        <element source="/etc/init.d/final3"/>
        <element source="/etc/init.d/final5"/>
        <element source="/etc/init.d/final8"/>

        <element source="/etc/default/locale"/>
        <element source="/etc/environment"/>
        <element source="/sbin/mountall"/> <!-- /etc/fstab is part of initrd -->
        <element source="/usr/sbin/irqbalance"/>
        
        <!-- dbus for avahi only -->
        <element source="/bin/dbus-daemon"/>
        <element source="/bin/dbus-uuidgen"/>
        <element source="/etc/dbus-1" type="dir" recurse="1" mask="*"/>
        <element source="/etc/init.d/dbus"/>
        <element source="/usr/share/dbus-1" type="dir" recurse="1" mask="*"/>
        <element source="/lib/dbus-1.0" type="dir" recurse="1" mask="*" version="lts10.04"/>
        <element source="/usr/lib/dbus-1.0" type="dir" recurse="1" mask="*" version="lts12.04"/>

        <element source="/usr/sbin/console-kit-daemon"/>
        <element source="/etc/ConsoleKit" type="dir" recurse="1" mask="*"/>
        <element source="/usr/lib/ConsoleKit" type="dir" recurse="1" mask="*"/>
        <element source="/lib/udev/udev-acl"/>
        <element source="/etc/ConsoleKit/run-seat.d" type="emptydir" />
        <element source="/etc/ConsoleKit/run-session.d" type="emptydir" />

        <!-- Watchdog -->
        <element source="/usr/sbin/watchdog" />
        <element source="/usr/sbin/wd_keepalive" />
        <element source="/etc/default/watchdog" />
        <element source="/etc/watchdog.conf" />
        <element source="/etc/init.d/watchdog" />
        <element source="/dev/watchdog" type="node" nodetype="c" major="10" minor="130" />
        
        <!-- kexec/kdump support -->
        <element source="/sbin/kexec"/>
        <element source="/etc/logrotate.d/vmcores"/>
                
        <!-- network -->
        <element source="/etc/network" type="dir" recurse="1" mask="*"/>
        <!--element source="/etc/network/if-down.d" type="emptydir" /-->
        <element source="/var/run/network" type="emptydir" />
        <element source="/sbin/dhclient"/>
        <element source="/sbin/dhclient-script"/>
        <element source="/sbin/dhclient3"/>
        <element source="/etc/dhcp3/dhclient.conf" />
        <element source="/etc/dhcp3/dhclient.conf" target="/etc/dhcp/dhclient.conf"/>
        <!--element source="/etc/dhcp3/dhclient-enter-hooks.d/update-cfg"/-->
        <element source="/etc/dhcp3/dhclient-enter-hooks.d/debug" version="lts10.04"/>
        <element source="/var/lib/dhcp3/" type="emptydir" />
        <include spec="pam.inc"/>
        
        <!-- Localization -->
        <element source="/usr/lib/locale" type="dir" recurse="1" mask="*"/>
        <element source="/usr/share/zoneinfo" type="dir" recurse="1" mask="*"/>
        <element source="/etc/ssl/certs" type="dir" recurse="1" mask="*"/>
        <element source="/etc/ssl/private/ssl-cert-snakeoil.key" group="106" perms="0440" />
        <element source="/lib/terminfo/l/linux" version="lts12.04" />
        <element source="/usr/share/terminfo/l/linux" version="lts10.04"  />
        <element source="/usr/share/terminfo/x" type="dir" mask="xterm.*" version="lts10.04" />
        <element source="/lib/terminfo/x" type="dir" mask="xterm.*"/>
        
        <!-- Openssl -->
        <element source="/usr/bin/openssl"/>
        <element source="/usr/bin/c_rehash"/>
        <element source="/usr/lib/ssl" type="dir" recurse="1" mask="*"/>
        <element source="/etc/ssl" type="dir" recurse="1" mask="*"/>
        <element source="/usr/lib/ssl" type="dir" recurse="1" mask="*"/>
        
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
                mkdir -p /etc/rc.d
                mkdir -p /etc/ssh
                cp /curroot/etc/hosts /etc/hosts 2>/dev/null
                cp /curroot/etc/passwd /etc/passwd 2>/dev/null
                cp /curroot/etc/shadow /etc/shadow 2>/dev/null
                cp /curroot/etc/group /etc/group 2>/dev/null
                cp /curroot/etc/gshadow /etc/gshadow 2>/dev/null
                cp /curroot/etc/ssh/*_key /etc/ssh 2>/dev/null
                cp /curroot/etc/ssh/*_key.pub /etc/ssh 2>/dev/null
                chmod 0400 /etc/ssh/*_key 2>/dev/null
                chmod 0440 /etc/sudoers.d/* 2>/dev/null
                echo $rimBuildLabel > /etc/${rimNode}-${rimApplication}-${rimProduct}-release 2>/dev/null
                #
                # Always perform these operations on the rw jail
                #
                mkdir -p /var/run
                mkdir -p /var/run/sshd
                mkdir -p /var/run/network
                mkdir -p /var/lib/update-rc.d
                touch /var/run/utmpx
                ln -s /tmp /var/tmp
                mkdir -p /var/log
                mkdir -p /var/empty/sshd
                mkdir -p /var/lib
                mkdir -p /var/evlog
                mkdir -p /var/spool/cron
                # at support
                mkdir /var/spool/cron/atjobs
                mkdir /var/spool/cron/atspool
                touch /var/spool/cron/atjobs/.SEQ
                chown -R daemon /var/spool/cron/atjobs /var/spool/cron/atspool
                mkdir -p /var/lock/subsys
                mkdir -p /var/run/netreport
                mkdir -p /etc/network/if-pre-up.d
                mkdir -p /etc/network/if-up.d
                #
                # dbus
                #
                prefix=/lib
                [ "$rimReleaseVersion" == "lts12.04" ] && prefix="/usr/lib"
                chown root $prefix/dbus-1.0/dbus-daemon-launch-helper
                chgrp messagebus $prefix/dbus-1.0/dbus-daemon-launch-helper
                chmod 4754 $prefix/dbus-1.0/dbus-daemon-launch-helper
                mkdir -p /var/run/dbus
                chown messagebus:messagebus /var/run/dbus
                #
                # Authbind helper needs to be setuid
                #
                chmod 4755 /usr/lib/authbind/helper
                #
                # generate the linkage for sysv init
                #
                setUpRcLinks
                groupadd -f -o -g ${ntpGid} ntp
                egrep -q "^ntp:" /etc/passwd || (
                    useradd -M \
                        -s /bin/false \
                        -u ${ntpUid} \
                        -g ${ntpGid} \
                        -c "NTP runtime user name" \
                        -d /home/ntp \
                        ntp
                ) 2>/dev/null 1>&2
                chown ntp /var/lib/ntp
                return 0
             ]]>
        </script>
        <script context="up" rank="20">
            <![CDATA[
                touch /var/run/utmpx
                return 0
             ]]>
        </script>
    </module>
</spec>
        
