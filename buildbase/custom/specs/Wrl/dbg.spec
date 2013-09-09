<?xml version="1.0" ?>
<spec version="1.0">
    <module name="dbg" version="1.0" flags="optional" level="9" fs="squashfs">
        <element source="/etc/tpdev"/>
        
        <element source="/usr/bin/pstack"/>
        
        <element source="/usr/share/file" type="dir" recurse="1" mask="*" />
        
        
        <element source="/usr/sbin/in.rlogind" />
        <element source="/usr/sbin/in.rshd" />
        <element source="/usr/sbin/lsof" />
        
        <element source="/etc/xinetd.d/rsh" perm="0644"/>
        <element source="/etc/xinetd.d/rlogin" perm="0644"/>
        
        <element source="/usr/share/terminfo/x" type="dir" mask="xterm.*" />
        <element source="/lib/terminfo/d/dumb" target="/usr/share/terminfo/d/dumb" />
        
        <!-- for support of threads in gdb -->
        <element source="/usr/bin/gdbserver" />
        <element source="/usr/bin/gdb" />
        <element source="/usr/lib/debug" type="dir" recurse="1" mask="*" />
        
        <element source="/usr/lib/libcurses.so"/>
        <element source="libcurses.so" target="/usr/lib/libtermcap.so" type="link"/>
        <element source="/usr/share/man" type="dir" recurse="1" mask="*"/>
        <element source="/rim/usr/share/man" type="dir" recurse="1" mask="*"/>
        
        <!-- crash dump analysis support on the box -->
        <element source="boot/kernel" target="/boot/kernel" perms="0755"/>
        <element source="boot/vmlinux" target="/boot/vmlinux" perms="0755"/>
        <element source="/usr/sbin/crash" perms="0755"/>
        <element source="/usr/lib/crash" type="dir" recurse="1" mask="*"/>
        <!--
            Test guys want these - START
            FIXME - need to create a test module which does not ship
        -->
        <element source="/usr/sbin/tcpdump" />
        <element source="//${BLDROOT}/tools/tcpdump/tcpdumplinux" target="/usr/sbin/tptcpdump" />
        <element source="/usr/bin/sftp" />
        <element source="/usr/bin/snmpwalk" />
        <element source="/usr/libexec/openssh/sftp-server" target="/usr/lib/sftp-server" />
        <!--
            Test guys want these - END
        -->
   </module>
</spec>
