<?xml version="1.0" ?>
<spec version="1.0">
    <module name="Python2.7" version="1.0" flags="required" level="3" fs="squashfs">
		<element source="/usr/bin/python2.7" perm="0755"/>
        <element source="python2.7" target="/usr/bin/python" type="link" />
		<element source="/usr/lib/python2.7" type="dir" recurse="1" mask="*" />
		<element source="/usr/include/python2.7" type="dir" recurse="1" mask="*" />
    </module>
</spec>
