<?xml version="1.0" ?>
<spec version="1.0">
    <module name="perl-5.8.7" version="1.0" flags="optional" level="3" fs="squashfs">
		<element source="/usr/bin/perl" perm="0755"/>
		<element source="/usr/lib/perl5" type="dir" recurse="1" mask="*"/>
    </module>
</spec>
