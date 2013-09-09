<?xml version="1.0" ?>
<spec version="1.0">
    <module name="perl-5.8.7" version="1.0" level="3" fs="squashfs">
		<element source="/usr/bin/perl" perm="0755"/>
		<element source="/usr/lib/perl/5.10.1" target="/usr/local/lib/perl/5.10.1" type="dir" recurse="1" mask="*"/>
		<element source="/usr/share/perl/5.10.1" target="/usr/local/share/perl/5.10.1" type="dir" recurse="1" mask="*"/>
    </module>
</spec>
