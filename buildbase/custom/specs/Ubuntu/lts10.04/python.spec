<?xml version="1.0" ?>
<spec version="1.0">
    <module name="python2.6" version="1.0" flags="optional" level="5" fs="squashfs">
		<element source="/usr/bin/python2.6" perm="0755"/>
        <element source="python2.6" target="/usr/bin/python" type="link" />
		<element source="/usr/lib/python2.6" type="dir" recurse="1" mask="*"/>
		<element source="/usr/lib/pymodules/python2.6" target="/usr/lib/python2.6/dist-packages" type="dir" recurse="1" mask="*"/>
		<element source="/usr/lib/python2.6/dist-packages" type="dir" recurse="1" mask="*"/>
		<element source="/usr/share/pyshared" type="dir" recurse="1" mask="*"/>
		<element source="/usr/lib/pyshared" type="dir" recurse="1" mask="*"/>
    </module>
    <module name="python2.7" version="1.0" flags="optional" level="5" fs="squashfs">
    
        <!-- Python package dependency checks -->
        <element source="/etc/depend/python-psycopg2"/>
        
		<element source="/usr/bin/python2.7" perm="0755"/>
        <element source="python2.7" target="/usr/bin/python" type="link" />
		<element source="/usr/lib/python2.7" type="dir" recurse="1" mask="*"/>
		<element source="/usr/include/python2.7" type="dir" recurse="1" mask="*"/>
		<element source="/usr/lib/python2.7/dist-packages" type="dir" recurse="1" mask="*"/>
		<element source="/usr/share/pyshared" target="/usr/lib/python2.7/dist-packages" type="dir" recurse="1" mask="*"/>
		<element source="/usr/share/python-support" type="dir" recurse="1" mask="*"/>
		<element source="/usr/lib/pyshared" type="dir" recurse="1" mask="*"/>
    </module>
</spec>
