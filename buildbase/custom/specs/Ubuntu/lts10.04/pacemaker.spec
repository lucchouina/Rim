<?xml version="1.0" ?>
<spec version="1.0">
    <module name="pacemaker-1.1.6" version="1.0" flags="optional" level="5" fs="squashfs">
        <element source="/var/lib/heartbeat" type="dir" recurse="1" mask="*" />
        <element source="/var/lib/pengine" type="dir" recurse="1" mask="*" />
        <element source="/usr/lib/ocf" type="dir" recurse="1" mask="*" />
        <element source="/usr/share/pacemaker" type="dir" recurse="1" mask="*" />
        <element source="/usr/lib/lcrso/pacemaker.lcrso" />
        <element source="/usr/share/pyshared/crm" type="dir" recurse="1" mask="*" />
        <element source="/usr/share/pyshared/cts" type="dir" recurse="1" mask="*" />
        <element source="/usr/lib/python2.7/dist-packages/crm" type="dir" recurse="1" mask="*" />
        <element source="/usr/lib/python2.7/dist-packages/cts" type="dir" recurse="1" mask="*" />
        <element source="/usr/share/pyshared/cts" type="dir" recurse="1" mask="*" />
        <element source="/usr/sbin/crm_verify"/>
        <element source="/usr/sbin/fence_legacy"/>
        <element source="/usr/sbin/crm_report"/>
        <element source="/usr/sbin/cibpipe"/>
        <element source="/usr/sbin/crm_mon"/>
        <element source="/usr/sbin/crm_uuid"/>
        <element source="/usr/sbin/crm_failcount"/>
        <element source="/usr/sbin/crm"/>
        <element source="/usr/sbin/crm_node"/>
        <element source="/usr/sbin/crmadmin"/>
        <element source="/usr/sbin/cibadmin"/>
        <element source="/usr/sbin/crm_ticket"/>
        <element source="/usr/sbin/crm_simulate"/>
        <element source="/usr/sbin/crm_master"/>
        <element source="/usr/sbin/crm_attribute"/>
        <element source="/usr/sbin/attrd_updater"/>
        <element source="/usr/sbin/stonith_admin"/>
        <element source="/usr/sbin/crm_shadow"/>
        <element source="/usr/sbin/crm_resource"/>
        <element source="/usr/sbin/pacemakerd"/>
        <element source="/usr/sbin/crm_diff"/>
        <element source="/usr/sbin/crm_standby"/>
        <element source="/usr/sbin/ptest"/>
        <element source="/usr/sbin/iso8601"/>
    </module>
</spec>
