<?xml version="1.0" ?>
<spec version="1.0">
<!--
    <element source="/sbin/pam_console_apply"/>
-->
	<element source="/etc/pam.d" type="dir" recurse="1" shadow="1" mask="*"/>
	<element source="/lib/security" type="dir" recurse="1" mask="*"/>
	<element source="/etc/security" type="dir" recurse="1" mask="*"/>
	<element source="/etc/securetty" perm="0400"/>
</spec>
