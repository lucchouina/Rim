<?xml version="1.0" ?>
<spec version="1.0">
    <module name="avahi-server" version="1.0" flags="optional" level="5" fs="squashfs">
    
        <!-- Avahi user names -->
        <var name="AvahiName" value="avahi"/>
        <var name="AvahiAutoIpName" value="avahi-autoipd"/>
        
		<element source="/etc/avahi/avahi-autoipd.action" />
		<element source="/etc/avahi/avahi-daemon.conf" />
		<element source="/etc/avahi/services" type="dir" recurse="1" mask="*" shadow="1" />
		<element source="/etc/avahi/hosts" />
		<element source="/etc/default/avahi-daemon" type="file" />
		<element source="/usr/share/avahi" type="dir" recurse="1" mask="*"/>
		<element source="/usr/sbin/avahi-daemon" type="file" />
        
		<element source="/usr/bin/avahi-publish-address" type="file" />
		<element source="/usr/bin/avahi-publish" type="file" />
		<element source="/usr/lib/avahi" type="dir" recurse="1" mask="*"/>
		<element source="/etc/network/if-post-down.d/avahi-daemon" type="file" />

        <!-- autoip included here -->
		<element source="/usr/sbin/avahi-autoipd" type="file" />

		<!-- Add rc support -->
		<var name="initScript" value="bonjour" />
		<element source="/etc/init.d/${initScript}" type="file" />
		<element source="/etc/bonjour.d" type="emptydir" />

        <script context="postinstall" rank="60">
            <![CDATA[
                mkdir -p /var/run/avahi-daemon
                groupadd -f ${AvahiName}
                egrep -q "^${AvahiName}:" /etc/passwd || (
                    useradd -M -g ${AvahiName} --password x -c "Avahi mDNS daemon" ${AvahiName}
                )  2>/dev/null 1>&2
                groupadd -f ${AvahiAutoIpName}
                egrep -q "^${AvahiAutoIpName}:" /etc/passwd || (
                    useradd -M -g ${AvahiAutoIpName} --password x -c "Avahi mDNS daemon" ${AvahiAutoIpName}
                )  2>/dev/null 1>&2
                return 0
             ]]>
        </script>
    </module>
</spec>
