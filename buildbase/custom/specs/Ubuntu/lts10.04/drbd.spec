<?xml version="1.0" ?>
<spec version="1.0">
    <module name="drbd8.3.11" version="1.0" flags="optional" level="5" fs="squashfs">
        <element source="/etc/drbd.d/global_common.conf"/>
        <element source="/etc/ha.d/resource.d/drbddisk"/>
        <element source="/etc/ha.d/resource.d/drbdupper"/>
        <element source="/etc/init.d/drbd"/>
        <element source="/etc/drbd.conf"/>
        <element source="/sbin/drbdsetup"/>
        <element source="/sbin/drbdadm"/>
        <element source="/sbin/drbdmeta"/>
        <element source="/usr/share/cluster/drbd.metadata"/>
        <element source="/usr/share/cluster/drbd.sh"/>
        <element source="/usr/sbin/drbd-overview"/>
        <element source="/usr/lib/ocf/resource.d/linbit/drbd"/>
        <element source="/usr/lib/drbd" type="dir" recurse="1" mask="*"/>
    </module>
</spec>
