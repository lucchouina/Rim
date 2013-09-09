<?xml version="1.0" ?>
<spec version="1.0">
    <module name="nfsserver-1.2.0" version="1.0" flags="optional" level="5" fs="squashfs">
        <element source="/etc/init.d/nfs-kernel-server"/>
        <element source="/etc/init.d/portmap"/>
        <element source="/usr/sbin/exportfs"/>
        <element source="/usr/sbin/rpc.mountd"/>
        <element source="/usr/sbin/rpc.nfsd"/>
        <element source="/usr/sbin/rpc.svcgssd"/>
        <element source="/sbin/showmount"/>
        <element source="/sbin/portmap"/>
        
        <!-- exportfs soils itself when thse emptry files cannot be found ...-->
        <element source="/var/lib/nfs/etab" type="emptyfile"/>
        <element source="/etc/exports" type="emptyfile"/>
        <element source="/var/lib/nfs/rmtab" type="emptyfile"/>
    </module>
</spec>
