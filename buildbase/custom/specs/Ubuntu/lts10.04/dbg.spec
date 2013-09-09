<?xml version="1.0" ?>
<spec version="1.0">
    <module name="dbg" version="1.0" flags="required" level="9" fs="squashfs">
        
        <element source="/usr/share/file" type="dir" recurse="1" mask="*" />
        <element source="/usr/bin/lsof" />
        <element source="/bin/fuser" />
        <element source="/usr/bin/ldd" />
        
        <!-- for support of threads in gdb -->
        <element source="/usr/bin/gdbserver" />
        <element source="/usr/bin/gdb" />

        <!--
            Test guys want these - START
            FIXME - need to create a test module which does not ship
        -->
        <element source="/usr/sbin/tcpdump" />
        <element source="/usr/bin/nslookup" />
        <element source="/usr/bin/sftp" />
        <element source="/usr/bin/ftp" />
        <element source="/usr/lib/openssh/sftp-server" target="/usr/lib/sftp-server" />
        <!--
            Test guys want these - END
        -->
   </module>
</spec>
