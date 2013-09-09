<?xml version="1.0" ?>
<spec version="1.0">
    <module name="dfw" version="1.0" flags="optional" level="2" prime="1" fs="squashfs">
        <!-- firewall [ dumb down firewall support - ufw is not that uncomplicated !! ] -->
        <element source="/etc/init.d/firewall"/>
        <element source="/etc/default/ufw" type="emptyfile"/>
        <element source="/etc/firewall.conf"/>
        <element source="/etc/firewall.d" type="emptydir"/>
        <element source="/sbin/firewall" target="/usr/sbin/ufw" type="link"/>
        <element source="/sbin/firewall" />
		<element source="/lib/xtables" type="dir" recurse="1" mask="*"/>        
        <element source="/sbin/iptables"/>
    </module>
</spec>
