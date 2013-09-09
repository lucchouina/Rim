<?xml version="1.0" ?>
<spec version="1.0">
    <module name="firewall" version="1.0" flags="optional" level="5" fs="squashfs">
        <!-- Ufw files -->
		<element source="/etc/logrotate.d/ufw" />
		<element source="/etc/rsyslog.d/20-ufw.conf" />
		<element source="/etc/ufw" type="dir" recurse="1" mask="*" />
		<element source="/etc/default/ufw" />
		<element source="/etc/init/ufw.conf" />
		<element source="/lib/ufw" type="dir" recurse="1" mask="*" />
		<element source="/usr/share/ufw" type="dir" recurse="1" mask="*" />
		<element source="/usr/sbin/ufw" />
        <!-- Iptables files -->
		<element source="/usr/bin/iptables-xml" perm="0755"/>
		<element source="/sbin/iptables" perm="0755"/>
		<element source="/sbin/iptables-restore" perm="0755"/>
		<element source="/sbin/iptables-save" perm="0755"/>
		<element source="/usr/sbin/iptables-apply" perm="0755"/>
		<element source="/usr/share/iptables" type="dir" recurse="1" mask="*"/>
		<element source="/lib/xtables" type="dir" recurse="1" mask="*"/>        
    </module>
</spec>
