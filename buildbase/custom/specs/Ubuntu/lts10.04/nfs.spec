<?xml version="1.0" ?>
<spec version="1.0">
    <module name="nfs-1.2.0" version="1.0" flags="optional" level="5" fs="squashfs">
        <element source="/etc/init.d/nfs-kernel-server"/>
        <element source="/usr/sbin/exportfs"/>
        <element source="/usr/sbin/rpc.mountd"/>
        <element source="/usr/sbin/rpc.nfsd"/>
        <element source="/usr/sbin/rpc.svcgssd"/>
        <element source="/sbin/showmount"/>
    </module>
</spec>
