<?xml version="1.0" ?>
<spec version="1.0">
    <module name="lighttpd" version="1.4.26-1" flags="optional" level="5" fs="squashfs">
		<element source="/var/www" type="emptydir" />
		<element source="/var/cache/lighttpd" type="emptydir" owner="www-data" group="www-data" parms="0750"/>
		<element source="/var/cache/lighttpd/compress" type="emptydir" owner="www-data" group="www-data" parms="0750"/>
		<element source="/var/cache/lighttpd/uploads" type="emptydir" owner="www-data" group="www-data" parms="0750"/>
		<element source="/etc/lighttpd/conf-available" type="dir" recurse="1" mask="*" />
		<element source="/etc/cron.daily/lighttpd" type="file" />

		<!-- Add rc support -->
		<var name="initScript" value="lighttpd" />
		<element source="/etc/init.d/${initScript}" type="file" />
        <element source="../init.d/${initScript}" target="/etc/rc5.d/S91${initScript}" type="link" />
        <element source="../init.d/${initScript}" target="/etc/rc1.d/K09${initScript}" type="link" />
        <element source="../init.d/${initScript}" target="/etc/rc6.d/K09${initScript}" type="link" />

		<element source="/etc/logrotate.d/lighttpd" type="file" />
		<element source="/usr/lib/cgi-bin" type="emptydir" />
		<element source="/usr/lib/lighttpd" type="dir" recurse="1" mask="*"/>
		<element source="/usr/share/lighttpd" type="dir" recurse="1" mask="*"/>
		<element source="/usr/sbin/lighttpd" type="file" />
		<element source="/usr/sbin/lighttpd-angel" type="file" />
		<element source="/usr/sbin/lighty-enable-mod" type="file" />
		<element target="/usr/sbin/lighttpd-disable-mod" source="lighty-enable-mod" type="link" />
		<element target="/usr/sbin/lighttpd-enable-mod" source="lighty-enable-mod" type="link" />
		<element target="/usr/sbin/lighty-disable-mod" source="lighty-enable-mod" type="link" />
        <script context="firstboot" rank="91">
            <![CDATA[
                mkdir -p /var/log/lighttpd
                chown www-data:www-data /var/log/lighttpd
                chmod 0750 /var/log/lighttpd
                return 0
             ]]>
        </script>
    </module>
</spec>
