<?xml version="1.0" ?>
<spec version="1.0">
    <module name="RimBase" version="1.0" flags="required" fs="squashfs" level="2" >
        <element source="src/sysv-init/init" target="/sbin/init"/>
        <element source="src/makedumpfile/makedumpfile" target="/sbin/makedumpfile" arch="arm" />
        <element source="init" target="/sbin/telinit" type="link"/>
        <element source="/sbin/initctl"/>
        <element source="initctl" target="/sbin/start"      type="link"/>
        <element source="initctl" target="/sbin/stop"       type="link"/>
        <element source="initctl" target="/sbin/restart"    type="link"/>
        <element source="initctl" target="/sbin/status"     type="link"/>
        <element source="initctl" target="/sbin/reload"     type="link"/>
        <element source="initctl" target="/sbin/service"     type="link"/>
        <element source="/etc/default/rcS"/>
        <element source="/etc/init.d/rcS"/>
        <element source="/etc/init.d/rc"/>
        <element source="/etc/inittab"/>
        <element source="/sbin/setUpRcLinks"/>
        <element source="/sbin/rcadm"/>
        <element source="/sbin/rcfilter"/>
        <element source="/sbin/rcEntries.py"/>
        <element source="/lib/lsb/init-functions"/>
        <element source="/sbin/start-stop-daemon"/>
        
        <!-- Rim startup/shutdown hook -->
        <element source="/etc/init.d/rim" />
        
        <!-- to handle the rimReset -->
        <element source="/etc/init.d/single" />
        
        <!-- Rim "firstboot but before db is up" script -->
        <element source="/etc/init.d/rimpredb" />
        <element source="/etc/init.d/postgresql" />
        
        <!-- Initmode webserver for level 3  -->
        <element source="/etc/init.d/initmode" />
        <!-- Appmode webserver for level 5  -->
        <element source="/etc/init.d/appmode" />
        
        <!-- Rim post install - script. Only for single media (arm/ SD) nodes-->
        <element source="/etc/init.d/rimpostinstall" />
        
        <!-- Network and general config -->
        <element source="/sbin/adminconsole"/>
        <element source="/sbin/insserv"/>
        <element source="/sbin/runhook"/>
        <element source="/sbin/update-rc.d"/>
        <element source="/sbin/getSystemSchema"/>
        <element source="/sbin/validateSystemInfo"/>
        <element source="/sbin/testSystemInfo"/>
        <element source="/sbin/translateSystemInfo"/>
        <element source="/sbin/getSystemInfo"/>
        <element source="/sbin/setSystemInfo"/>
        <element source="/sbin/webServer"/>
        <element source="/etc/loading.gif"/>
        <element source="/sbin/settings" type="dir" recurse="1" mask="*" skip="handlers"/>
        <element source="/sbin/settings/handlers/ipinfo.py"/>
        <element source="/sbin/settings/handlers/timeinfo.py"/>
        <element source="/sbin/settings/handlers/dns.py"/>
        <element source="/sbin/settings/handlers/system.py"/>
        <element source="/sbin/settings/handlers/build.py"/>
        <element source="/sbin/settings/handlers/__init__.py" type="emptyfile"/>
        
        <!-- Python support script -->
        <element source="scripts" target="/usr/lib/python2.6" type="dir" recurse="1" mask="*" version="lts10.04"/>
        <element source="scripts" target="/usr/lib/python2.7" type="dir" recurse="1" mask="*" version="lts12.04"/>
        
        <!-- configuration editing support (modified jsonwidget)   -->
        <element source="python/usr/bin" target="/usr/bin" type="dir" recurse="1" mask="*" />
        <element source="python/usr/share/pyshared" target="/usr/lib/python2.7" type="dir" recurse="1" mask="*" version="lts12.04"/>
        <element source="python/usr/share/pyshared" target="/usr/lib/python2.6" type="dir" recurse="1" mask="*" version="lts10.04"/>
        
        <script context="firstboot" rank="20">
            <![CDATA[
                return 0
             ]]>
        </script>
        <!-- stubs to make sure we have at least one of these during bringup -->
        <script context="firstbootpredb" rank="20">
            <![CDATA[
                return 0
             ]]>
        </script>
        <script context="postinstall" rank="1">
            <![CDATA[
                # transfer config
                [ -f /etc/hostname ] ||  echo $rimNode > /etc/hostname
                if [ -d /curroot/etc ]
                then
                    cp /curroot/etc/hostname /etc/hostname 2>/dev/null
                    ((chroot /curroot getSystemInfo) | translateSystemInfo | setSystemInfo -f -n)
                fi
                /bin/hostname -b -F /etc/hostname
                grep -q `hostname` /etc/hosts || echo "127.0.0.1 `hostname`" >> /etc/hosts
                if [ ! -f /etc/revert.cfg ] 
                then
                    if [ -f /curroot/etc/revert.cfg ]
                    then
                        # upgrade case - move original forward
                        cp /curroot/etc/revert.cfg  /etc/revert.cfg
                    else
                        getSystemInfo IPInfo System DNS > /etc/revert.cfg
                    fi
                fi
                # tftp
                echo tcp 80 ACCEPT > /etc/firewall.d/initmode
                # dhcp
                echo udp 81 ACCEPT >> /etc/firewall.d/initmode
                return 0
             ]]>
        </script>
        <script context="up" rank="10">
            <![CDATA[
                return 0
             ]]>
        </script>
        <script context="down" rank="90">
            <![CDATA[
                return 0
             ]]>
        </script>
        <script context="setvars" rank="0">
            <![CDATA[
                return 0
             ]]>
        </script>
    </module>
</spec>
