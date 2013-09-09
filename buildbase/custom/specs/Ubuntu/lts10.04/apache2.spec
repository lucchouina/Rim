<?xml version="1.0" ?>
<spec version="1.0">
    <module name="apache2" version="1.0" flags="optional" level="5" fs="squashfs">

		<element source="/etc/apache2" type="dir" recurse="1" mask="*" />
		<element source="/etc/bash_completion.d/apache2.2-common" type="file" />
		<element source="/etc/cron.daily/apache2" type="file" />
		<element source="/etc/default/apache2" type="file" />
		<element source="/etc/logrotate.d/apache2" type="file" />
		<element source="/etc/ufw/applications.d/apache2.2-common" type="file" />
		<element source="/usr/lib/apache2" type="dir" recurse="1" mask="*" />
		<element source="/usr/lib/cgi-bin" type="emptydir" />
		<element source="/etc/mime.types" type="file" />
        
        <!-- /usr/sbin -->
		<element source="/usr/sbin/apache2" type="file" />
		<element source="/usr/sbin/a2dismod" type="file" />
		<element source="/usr/sbin/a2dissite" type="file" />
		<element source="/usr/sbin/a2enmod" type="file" />
		<element source="/usr/sbin/a2ensite" type="file" />
		<element source="/usr/sbin/ab" type="file" />
		<element source="/usr/sbin/apache2ctl" type="file" />
		<element source="/usr/sbin/check_forensic" type="file" />
		<element source="/usr/sbin/checkgid" type="file" />
		<element source="/usr/sbin/htcacheclean" type="file" />
		<element source="/usr/sbin/httxt2dbm" type="file" />
		<element source="/usr/sbin/logresolve" type="file" />
		<element source="/usr/sbin/rotatelogs" type="file" />
		<element source="/usr/sbin/split-logfile" type="file" />
		<element source="/usr/share/apache2" type="dir" recurse="1" mask="*" />
                
        <!-- var -->
		<element source="/var/cache/apache2/mod_disk_cache" type="emptydir" owner="www-data" group="www-data" />
		<element source="/var/cache/apache2" type="emptydir" owner="www-data" group="www-data" />
		<element source="/var/log/apache2" type="emptydir" />
		<element source="/var/www" type="emptydir" />
        
        <!-- startup - classic sysv rc stuff (no upstart) -->
        <var name="initScript" value="apache2" />
        <element source="/etc/init.d/${initScript}" />
    </module>
</spec>
