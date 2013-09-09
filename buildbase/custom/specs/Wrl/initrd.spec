<?xml version="1.0" ?>
<spec version="1.0">
    <module name="initrd" version="1.0" required="1" bootable="1"  level="1" fs="squashfs">
        <!-- / -->
        <element source="/init" />
        
        <!-- Libs -->
        <element source="/lib/libnss_files.so.2"/>
        <element source="/lib/libnss_compat.so.2"/>
        <element source="/lib/modules/2.6.27.39/modules.dep"/>
        
        <!-- bin -->
        <element source="/bin/awk"/>   
        <element source="/bin/bash"/>   
        <element source="/bin/cat"/>
        <element source="/bin/chmod"/>
        <element source="/bin/cp"/>
        <element source="/bin/dd"/>
        <element source="/bin/dmesg"/>
        <element source="/bin/df"/>
        <element source="/bin/grep"/>
        <element source="/bin/gzip"/>
        <element source="/bin/gunzip"/>
        <element source="/bin/hostname"/>
        <element source="/bin/ln"/>
        <element source="/bin/login"/>
        <element source="/bin/logger" />
        <element source="/bin/ls"/>
        <element source="/bin/lsmod"/>
        <element source="/bin/mkdir"/>
        <element source="/bin/mknod"/>
        <element source="/bin/mount"/>
        <element source="/bin/mv"/>
        <element source="/bin/netstat"/>
        <element source="/bin/openvt"/>
        <element source="/bin/ping"/>
        <element source="/bin/ps"/>
        <element source="/bin/rm"/>
        <element source="/bin/sed"/>
        <element source="/bin/sleep"/>
        <element source="/bin/stty"/>
        <element source="/bin/su"/>
        <element source="/bin/tar"/>
        <element source="/bin/touch"/>
        <element source="/bin/true"/>
        <element source="/bin/umount"/>
        <element source="/bin/uname"/>
        
        <!-- sbin -->
        <element source="/sbin/agetty"/>
        <element source="/sbin/consoletype"/>
        <element source="/sbin/depmod"/>
        <element source="/sbin/e2label"/>
        <element source="/sbin/fdisk"/>
        <element source="/sbin/fsck"/>
        <element source="/sbin/fsck.ext2"/>
        <element source="/sbin/fsck.ext3"/>
        <element source="/sbin/fstab-decode"/>
        <element source="/sbin/grub"/>
        <element source="/sbin/halt"/>
        <element source="/sbin/ifconfig"/>
        <element source="/sbin/ifenslave"/>
        <element source="/sbin/init"/>
        <element source="/sbin/insmod"/>
        <element source="/sbin/installRim"/>
        <element source="/sbin/ip"/>
        <element source="/sbin/killall5"/>
        <element source="/sbin/killall5" target="/bin/pidof" type="link"/>
        <element source="/sbin/losetup"/>
        <element source="/sbin/mdadm"/>
        <element source="/sbin/mingetty"/>
        <element source="/sbin/mkfs"/>
        <element source="/sbin/mkfs.ext2"/>
        <element source="/sbin/mkfs.ext3"/>
        <element source="/sbin/mkswap"/>
        <element source="/sbin/modinfo" />
        <element source="/sbin/modprobe" />
        <element source="/sbin/mount.nfs" />
        <element source="/sbin/mountVersion" />
        <element source="/sbin/pivot_root"/>
        <element source="/sbin/portmap"/>
        <element source="/sbin/reboot"/>
        <element source="/sbin/rebuildRaid"/>
        <element source="/sbin/rimboot"/>
        <element source="/sbin/rimFuncs"/>
        <element source="/sbin/rmmod"/>
        <element source="/sbin/route"/>
        <element source="/sbin/runlevel"/>
        <element source="/sbin/scratchInstall"/>
        <element source="/sbin/scsi_id"/>
        <element source="/sbin/setUpDisk"/>
        <element source="/sbin/sfdisk"/>
        <element source="/sbin/start_udev"/>
        <element source="/sbin/sysctl" />
        <element source="/sbin/tune2fs"/>
        <element source="/sbin/udevadm"/>
        <element source="/sbin/udevcontrol"/>
        <element source="/sbin/udevd"/>
        <element source="/sbin/udevsettle"/>
        <element source="/sbin/udevtrigger"/>

        <!-- usr/bin -->
        <element source="/usr/bin/dirname"/>
        <element source="/usr/bin/head"/>
        <element source="/usr/bin/id"/>
        <element source="/usr/bin/killall"/>
        <element source="/usr/bin/scp"/>
        <element source="/usr/bin/ssh"/>
        <element source="/usr/bin/stat"/>
        <element source="/usr/bin/strace"/>
        <element source="/usr/bin/tail"/>
        <element source="/usr/bin/tty"/>
        <element source="/usr/bin/tftp"/>
        <element source="/usr/bin/tr"/>
        <element source="/usr/bin/ipmitool"/>

        <!-- usr/sbin -->
        <element source="/usr/sbin/arping"/>
        <element source="/usr/sbin/chroot"/>
        <element source="/usr/sbin/ipmievd"/>
        <element source="/usr/sbin/ipmiutil"/>
        
        <!-- etc -->
        <element source="/etc/fstab"/>
        <element source="/etc/group"/>
        <element source="/etc/gshadow" perm="0700" />
        <element source="/etc/hosts"/>
        <element source="/etc/inittab"/>
        <element source="/etc/issue"/>
        <element source="/etc/login.defs"/>
        <element source="/etc/nsswitch.conf"/>
        <element source="/etc/passwd"/>
        <element source="/etc/profile"/>
        <element source="/etc/scsi_id.config"/>
        <element source="/etc/services"/>
        <element source="/etc/shadow" perm="0700" />
        <element source="/etc/sysctl.conf" />
        <element source="/etc/udev/udev.conf" />
        
        <!-- misc -->
        <element source="bash"               	target="/bin/sh"            type="link"/>
        <element source="bash"               	target="/bin/sh2"            type="link"/>
        <element source="/soft"                 type="emptydir" perm="0755" />
        <element source="/selinux"              type="dir" perm="0755" />
        <element source="/data"                 type="emptydir" perm="0755" />
        <element source="/tmp"                  type="dir" perm="01755" />
        <element source="/proc"                 type="emptydir" perm="0755" />
        <element source="/root"                 type="emptydir" perm="0755" />
        <element source="/sys"                  type="emptydir" perm="0755" />
        <element source="/dev"                  type="emptydir" perm="0755" />
        <element source="data/home"             target="/home" type="link" />
        <element source="/mnt"                  type="emptydir" perm="0755" />
        <element source="/etc/udev"             type="emptydir" recurse="1" mask="*"/>
        
        <!-- Link below is crutial to using mkfs -t ext3... -->
        <element source="/proc/mounts"          target="/etc/mtab"          type="link"/>
        <element source="/boot/grub"            type="dir"  recurse="1"     mask="*"    cpu="i386"/>
        <element source="/usr/lib/grub"         type="dir"  recurse="1"     mask="*"    cpu="i386"/>
        <element source="/dev/console"          type="node" nodetype="c"    major="5"   minor="1" />
        <element source="/dev/null"             type="node" nodetype="c"    major="1"   minor="3" />
        <element source="/dev/zero"             type="node" nodetype="c"    major="1"   minor="5" />
		<include spec="pam.inc"/>
    </module>
</spec>
