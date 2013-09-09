<?xml version="1.0" ?>
<spec version="1.0">
    <module name="pacemaker-1.1.6" version="1.0" flags="optional" level="5" fs="squashfs">
        <element source="/etc/corosync" type="dir" recurse="1" mask="*" />
        <element source="/usr/lib/lcrso/coroparse.lcrso" />
        <element source="/usr/lib/lcrso/vsf_ykd.lcrso" />
        <element source="/usr/lib/lcrso/vsf_quorum.lcrso" />
        <element source="/usr/lib/lcrso/service_pload.lcrso" />
        <element source="/usr/lib/lcrso/service_cpg.lcrso" />
        <element source="/usr/lib/lcrso/objdb.lcrso" />
        <element source="/usr/lib/lcrso/service_cfg.lcrso" />
        <element source="/usr/lib/lcrso/service_confdb.lcrso" />
        <element source="/usr/lib/lcrso/quorum_testquorum.lcrso" />
        <element source="/usr/lib/lcrso/quorum_votequorum.lcrso" />
        <element source="/usr/lib/lcrso/service_evs.lcrso" />
        <element source="/etc/default/corosync" />
        <element source="/etc/logrotate.d/corosync" />
        <element source="/etc/init.d/corosync" />
        <element source="/var/lib/corosync" type="dir" recurse="1" mask="*" />
        <element source="/usr/sbin/corosync" />
        <element source="/usr/sbin/corosync-notifyd" />
        <element source="/usr/sbin/corosync-objctl" />
        <element source="/usr/sbin/corosync-cpgtool" />
        <element source="/usr/sbin/corosync-quorumtool" />
        <element source="/usr/sbin/corosync-fplay" />
        <element source="/usr/sbin/corosync-pload" />
        <element source="/usr/sbin/corosync-keygen" />
        <element source="/usr/sbin/corosync-cfgtool" />
        <element source="/usr/bin/corosync-blackbox" />
    </module>
</spec>
