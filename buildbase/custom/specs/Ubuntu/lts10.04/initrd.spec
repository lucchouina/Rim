<?xml version="1.0" ?>
<spec version="1.0">
    <module name="initrd" version="1.0" flags="required" bootable="1"  level="1" fs="squashfs">

        <!-- /init is a Rim specific script from rim/custom/init -->
        <element source="/init"/>
        
        <!-- Libs -->
        <element source="/lib/libnss_files.so.2" version="lts10.04"/>
        <element source="/lib/x86_64-linux-gnu" type="dir" recurse="1" mask="*" arch="x86_64" version="lts12.04"/>
        <element source="/lib64" type="dir" recurse="1" mask="*" arch="x86_64" version="lts12.04"/>
        <!--element source="/lib/x86_64-linux-gnu/libnss_files.so.2" arch="x86_64" version="lts12.04"/-->
        <element source="/lib/libnss_compat.so.2" version="lts10.04"/>
        <!--element source="/lib/x86_64-linux-gnu/libnss_compat.so.2" arch="x86_64" version="lts12.04"/-->
        <element source="/lib" target="/lib64" type="link"  version="lts10.04"/>
        <element source="/usr/lib" target="/usr/lib64" type="link" version="lts10.04"/>
        <element source="/lib/ld-linux-x86-64.so.2" version="lts10.04"/>
        <!-- bin -->
        <element source="/usr/bin/awk"/>   
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
        <element source="/bin/ip"/>
        <element source="/bin/ln"/>
        <element source="/bin/login"/>
        <element source="/usr/bin/logger" />
        <element source="/bin/ls"/>
        <element source="/bin/lsmod"/>
        <element source="/bin/mkdir"/>
        <element source="/bin/mknod"/>
        <element source="/bin/mount"/>
        <element source="/bin/mv"/>
        <element source="/bin/netstat"/>
        <element source="/bin/openvt"/>
        <var name="pingexe" value="/bin/ping"/>
        <element source="${pingexe}"/>
        <element source="/bin/ps"/>
        <element source="/bin/rm"/>
        <element source="/bin/sed"/>
        <element source="/bin/sleep"/>
        <element source="/bin/stty"/>
        <element source="/bin/su"/>
        <element source="/bin/sync"/>
        <element source="/bin/tar"/>
        <element source="/bin/touch"/>
        <element source="true" target="/bin/quiet" type="link"/>
        <element source="true" target="/bin/rw"  type="link"/>
        <element source="/bin/true"/>
        <element source="/bin/umount"/>
        <element source="/bin/uname"/>
        
        <!-- sbin -->
        <element source="/sbin/getty"/>
        <element source="/sbin/depmod"/>
        <element source="/sbin/e2label"/>
        <element source="/sbin/fdisk"/>
        <element source="/sbin/fsck"/>
        <element source="/sbin/fsck.ext2"/>
        <element source="/sbin/fsck.ext3"/>
        <element source="/sbin/fstab-decode"/>
        <element source="/sbin/ifconfig"/>
        <element source="/sbin/insmod"/>
        <element source="/sbin/kexec"/>
        <element source="/sbin/kdump"/>
        <element source="/sbin/killall5"/>
        <element source="/sbin/killall5" target="/bin/pidof" type="link"/>
        <element source="/sbin/losetup"/>
        <element source="/sbin/mdadm"/>
        <element source="/sbin/mkfs"/>
        <element source="/sbin/mkfs.ext2"/>
        <element source="/sbin/mkfs.ext3"/>
        <element source="/sbin/mkswap"/>
        <element source="/sbin/modinfo" />
        <element source="/sbin/modprobe" />
        <element source="/sbin/mount.nfs" arch="i386 x86_64" />
        <element source="/sbin/pivot_root"/>
        <element source="/sbin/reboot"/>
        <element source="/sbin/reboot" target="/sbin/poweroff"  type="link"/>
        <element source="/sbin/reboot" target="/sbin/halt"      type="link"/>
        <element source="/sbin/rmmod"/>
        <element source="/sbin/route"/>
        <element source="/sbin/runlevel"/>
        <element source="/sbin/sfdisk"/>
        <element source="/sbin/sulogin"/>
        <element source="/sbin/swapon"/>
        <element source="/sbin/swapoff"/>
        <element source="/sbin/tune2fs"/>
        <element source="/sbin/sysctl" />
        
        <!-- Rim utilities -->
        <element source="/sbin/mountVersion" />
        <element source="/sbin/installRim"/>
        <element source="/sbin/upgrade"/>
        <element source="/sbin/downgrade"/>
        <element source="/sbin/doPostInstall"/>
        <element source="/sbin/runAction"/>
        <element source="/sbin/rimboot"/>
        <element source="/sbin/rimReset"/>
        <element source="/sbin/rimDoReset"/>
        <element source="/sbin/rimAppVersion"/>
        <element source="/sbin/rimFuncs"/>
        <element source="/sbin/rebuildRaid"/>
        <element source="/sbin/scratchInstall"/>
        <element source="/sbin/setUpDisk"/>
        <element source="/sbin/unMountVersion" />      

        <!-- usr/bin -->
        <element source="/usr/bin/dirname"/>
        <element source="/usr/bin/eject"/>
        <element source="/usr/bin/head"/>
        <element source="/usr/bin/id"/>
        <element source="/usr/bin/killall"/>
        <element source="/usr/bin/lshw"/>
        <element source="/usr/bin/scp"/>
        <element source="/usr/bin/ssh"/>
        <element source="/usr/bin/stat"/>
        <element source="/usr/bin/strace"/>
        <element source="/usr/bin/tail"/>
        <element source="/usr/bin/tty"/>
        <element source="/usr/bin/tftp"/>
        <element source="/usr/bin/tr"/>
        <element source="/usr/bin/ipmitool" arch="i386 x86_64" />

        <!-- usr/sbin -->
        <element source="/usr/sbin/chroot"/>
        <element source="/usr/sbin/ipmievd" arch="i386 x86_64"/>
        
        <!-- etc -->
        <element source="/lib/init/fstab"/>
        <element source="/etc/fstab" type="emptyfile"/>
        <element source="/etc/group"/>
        <element source="/etc/gshadow" perm="0700" />
        <element source="/etc/hosts"/>
        <element source="/etc/issue"/>
        <element source="/etc/login.defs"/>
        <element source="/etc/nsswitch.conf"/>
        <element source="/etc/passwd"/>
        <element source="/etc/protocols"/>
        <element source="/etc/rpc"/>
        <element source="/etc/netconfig" version="lts12.04"/>
        <element source="/etc/profile"/>
        <element source="/etc/services"/>
        <element source="/etc/shadow" perm="0700" />
        <element source="/etc/sysctl.conf" />
        <element source="/etc/sysctl.d" type="dir" recurse="1" mask="*" />
        
        <!-- Grub -->
        <element source="/usr/sbin/grub" arch="i386 x86_64"/>
        <element source="/usr/lib/grub/i386-pc" target="/boot/grub" type="dir" recurse="1" mask="*" arch="i386" />
        <element source="/usr/lib/grub/x86_64-pc" target="/boot/grub" type="dir" recurse="1" mask="*" arch="x86_64" />
        <element source="/lib/modules/3.1.1-Atom-1.0/modules.dep" type="emptyfile" />

        <!-- misc -->
        <element source="bash"               	target="/bin/sh"            type="link"/>
        <element source="bash"               	target="/bin/sh2"           type="link"/>
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
        
        <!-- /init hook for starting udev -->
        <element source="/sbin/start_udev" />
        <element source="/etc/udev"             type="emptydir" />
        <element source="/run/udev"             type="emptydir" perms="0777" />
        <element source="/etc/udev/udev.conf" />
        <element source="/sbin/udevadm"/>
        <element source="/sbin/udevd"/>
        <element source="/lib/udev/rules.d/50-udev-default.rules" target="/lib/udev/rules.d/50-udev-default.rules" />

        <!-- Link below is crutial to using mkfs -t ext3... -->
        <element source="/proc/mounts"          target="/etc/mtab"          type="link"/>
        <element source="/dev/console"          type="node" nodetype="c"    major="5"   minor="1" />
        <element source="/dev/null"             type="node" nodetype="c"    major="1"   minor="3" />
        <element source="/dev/zero"             type="node" nodetype="c"    major="1"   minor="5" />
        <element source="/dev/urandom"          type="node" nodetype="c"    major="1"   minor="9" />
        <script context="postinstall" rank="15">
            <![CDATA[
                # due to squashfs limit on setuid attributes we need to do certain things
                # at install time...
                # switcharoo to create a ext2 file
                cp ${pingexe} ${pingexe}.tmp
                mv ${pingexe}.tmp ${pingexe} 
                chmod 4755 ${pingexe}
                return 0
             ]]>
        </script>
    </module>
</spec>
