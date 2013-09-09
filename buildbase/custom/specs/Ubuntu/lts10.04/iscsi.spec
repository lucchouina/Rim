<?xml version="1.0" ?>
<spec version="1.0">
    <module name="iscsi-2.0" version="1.0" flags="optional" level="5" fs="squashfs">
        <element source="/sbin/iscsiadm"/>
        <element source="/etc/init.d/open-iscsi"/>
        <element source="/etc/iscsi/iscsid.conf"/>
        <element source="/etc/iscsi/initiatorname.iscsi"/>
        <element source="/sbin/iscsid"/>
        <element source="/sbin/iscsi-iname"/>
        <element source="/sbin/iscsistart"/>
        <script context="postinstall" rank="43">
            <![CDATA[
	            MACAddr=`ifconfig eth0 | sed -n -e 's/://g' -e 's/.*HWaddr *\([0-9a-z]*\)/\1/p'`
	            if [ -n "$MACAddr" ]; then
		            sed -i -e '/InitiatorName/s/iqn.2010-08.org.github:/iqn.2013-09.org.rim:/' \
				            -e "/InitiatorName/s/:01:.*/:01:$MACAddr/" /etc/iscsi/initiatorname.iscsi
	            fi
                mkdir -p /run/lock
                return 0
             ]]>
        </script>
    </module>
</spec>
