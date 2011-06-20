import os
import iutil
import types
import re
import shutil
import logging
import glob
log = logging.getLogger("anaconda")

def abiquoPostInstall(anaconda):
    log.info("Abiquo 1.8 post")

    # loopback up
    iutil.execWithRedirect("/sbin/ifconfig",
                            ['lo', 'up'],
                            stdout="/mnt/sysimage/var/log/abiquo-postinst.log", stderr="//mnt/sysimage/var/log/abiquo-postinst.log",
                            root=anaconda.rootPath)

    if (anaconda.backend.isGroupSelected('abiquo-kvm') or \
            anaconda.backend.isGroupSelected('abiquo-xen') or \
            anaconda.backend.isGroupSelected('abiquo-virtualbox') or \
            anaconda.backend.isGroupSelected('abiquo-v2v') or \
            anaconda.backend.isGroupSelected('abiquo-remote-services')) and \
            not anaconda.backend.isGroupSelected('abiquo-nfs-repository'):
                f = open(anaconda.rootPath + "/etc/fstab", "a")
                f.write("%s /opt/vm_repository  nfs defaults    0 0\n" %
                            anaconda.id.abiquo_rs.abiquo_nfs_repository )
                f.close()
    
    if anaconda.backend.isGroupSelected('cloud-in-a-box'):
        f = open(anaconda.rootPath + "/opt/abiquo/config/abiquo.properties", "a")
        f.write("abiquo.virtualfactory.kvm.fullVirt = false\n")
        f.close()
    

    if anaconda.backend.isGroupSelected('abiquo-dhcp-relay'):
        vrange1 = anaconda.id.abiquo.abiquo_dhcprelay_vrange_1
        vrange2 = anaconda.id.abiquo.abiquo_dhcprelay_vrange_2
        mgm_if = anaconda.id.abiquo.abiquo_dhcprelay_management_if
        service_if = anaconda.id.abiquo.abiquo_dhcprelay_service_if
        dhcpd_ip = anaconda.id.abiquo.abiquo_dhcprelay_dhcpd_ip
        relay_net = anaconda.id.abiquo.abiquo_dhcprelay_service_network 
        log.info("abiquo-dhcp-relay %s %s %s %s %s %s %s %s %s %s" % ('-r', mgm_if, '-s', service_if, '-v', "%s-%s" % (vrange1, vrange2), '-x', dhcpd_ip, '-n', relay_net))
        iutil.execWithRedirect("/usr/bin/abiquo-dhcp-relay",
                            ['-r', mgm_if, '-s', service_if, '-v', "%s-%s" % (vrange1, vrange2), '-x', dhcpd_ip, '-n', relay_net],
                            stdout="/mnt/sysimage/var/log/abiquo-postinst.log", stderr="//mnt/sysimage/var/log/abiquo-postinst.log",
                            root=anaconda.rootPath)
        shutil.move(anaconda.rootPath + '/relay-config', anaconda.rootPath + '/etc/init.d/relay-config')
        iutil.execWithRedirect("/sbin/chkconfig",
                                ['relay-config', "on"],
                                stdout="/dev/tty5", stderr="/dev/tty5",
                                root=anaconda.rootPath)


    if anaconda.backend.isGroupSelected('abiquo-nfs-repository'):
        f = open(anaconda.rootPath + "/etc/exports", "a")
        f.write("/opt/vm_repository    *(rw,no_root_squash,subtree_check,insecure)\n")
        f.close()
        iutil.execWithRedirect("/sbin/chkconfig",
                                ['nfs', "on"],
                                stdout="/dev/tty5", stderr="/dev/tty5",
                                root=anaconda.rootPath)
        if not os.path.exists(anaconda.rootPath + '/opt/vm_repository'):
            os.makedirs(anaconda.rootPath + '/opt/vm_repository')
        if not os.path.exists(anaconda.rootPath + '/opt/vm_repository/.abiquo_repository'):
            open(anaconda.rootPath + '/opt/vm_repository/.abiquo_repository', 'w').close()

    if anaconda.backend.isGroupSelected('abiquo-remote-services'):
        iutil.execWithRedirect("/sbin/chkconfig",
                                ['dhcpd', "on"],
                                stdout="/dev/tty5", stderr="/dev/tty5",
                                root=anaconda.rootPath)

    if anaconda.backend.isGroupSelected('abiquo-server') or \
            anaconda.backend.isGroupSelected('cloud-in-a-box'):
                iutil.execWithRedirect("/sbin/chkconfig",
                                        ['rabbitmq-server', "on"],
                                        stdout="/dev/tty5", stderr="/dev/tty5",
                                        root=anaconda.rootPath)
                # start MySQL to create the schema
                iutil.execWithRedirect("/etc/init.d/mysqld",
                                        ['start'],
                                        stdout="/mnt/sysimage/var/log/abiquo-postinst.log", stderr="//mnt/sysimage/var/log/abiquo-postinst.log",
                                        root=anaconda.rootPath)

                iutil.execWithRedirect("/sbin/chkconfig",
                                        ['mysqld', "on"],
                                        stdout="/dev/tty5", stderr="/dev/tty5",
                                        root=anaconda.rootPath)
                
                # create the schema
                schema = open(anaconda.rootPath + "/usr/share/doc/abiquo-server/database/kinton-schema.sql")
                iutil.execWithRedirect("/usr/bin/mysql",
                                        [],
                                        stdin=schema,
                                        stdout="/mnt/sysimage/var/log/abiquo-postinst.log", stderr="//mnt/sysimage/var/log/abiquo-postinst.log",
                                        root=anaconda.rootPath)
                schema.close()

                # setup db credentials
                iutil.execWithRedirect("/usr/bin/abicli",
                                        ['set', 'database-password', ''],
                                        stdout="/dev/tty5", stderr="/dev/tty5",
                                        root=anaconda.rootPath)

    # Tweak security limits.conf file
    slimits = open(anaconda.rootPath + "/etc/security/limits.conf", 'a')
    slimits.write("root soft nofile 4096\n")
    slimits.write("root hard nofile 10240\n")
    slimits.close()


    if anaconda.backend.isGroupSelected('cloud-in-a-box') or \
            anaconda.backend.isGroupSelected('abiquo-lvm-storage-server'):
                iutil.execWithRedirect("/sbin/chkconfig",
                            ['tgtd', "on"],
                            stdout="/dev/tty5", stderr="/dev/tty5",
                            root=anaconda.rootPath)
                iutil.execWithRedirect("/sbin/chkconfig",
                                        ['abiquo-lvmiscsi', "on"],
                                        stdout="/dev/tty5", stderr="/dev/tty5",
                                        root=anaconda.rootPath)

    if anaconda.backend.isGroupSelected('abiquo-remote-services'):
        iutil.execWithRedirect("/sbin/chkconfig",
                                ['redis', "on"],
                                stdout="/dev/tty5", stderr="/dev/tty5",
                                root=anaconda.rootPath)
    if anaconda.backend.isGroupSelected('cloud-in-a-box'):
        iutil.execWithRedirect("/sbin/chkconfig",
                                ['nfs', "on"],
                                stdout="/dev/tty5", stderr="/dev/tty5",
                                root=anaconda.rootPath)
        iutil.execWithRedirect("/sbin/chkconfig",
                                ['iptables', "on"],
                                stdout="/dev/tty5", stderr="/dev/tty5",
                                root=anaconda.rootPath)
        iutil.execWithRedirect("/sbin/chkconfig",
                                ['dhcpd', "on"],
                                stdout="/dev/tty5", stderr="/dev/tty5",
                                root=anaconda.rootPath)
        iutil.execWithRedirect("/sbin/chkconfig",
                                ['smb', "on"],
                                stdout="/dev/tty5", stderr="/dev/tty5",
                                root=anaconda.rootPath)
        iutil.execWithRedirect("/sbin/chkconfig",
                                ['redis', "on"],
                                stdout="/dev/tty5", stderr="/dev/tty5",
                                root=anaconda.rootPath)
        open(anaconda.rootPath + '/opt/vm_repository/.abiquo_repository', 'w').close()
    if anaconda.backend.isGroupSelected('abiquo-kvm') or \
        anaconda.backend.isGroupSelected('cloud-in-a-box') or \
        anaconda.backend.isGroupSelected('abiquo-virtualbox'):
            iutil.execWithRedirect("/sbin/chkconfig",
                                ['avahi-daemon', "off"],
                                stdout="/dev/tty5", stderr="/dev/tty5",
                                root=anaconda.rootPath)
            f = open(anaconda.rootPath + "/etc/abiquo-aim.ini", "w")
            f.write("""
# AIM configuration file

[server]
port = 8889

[monitor]
uri = "qemu+unix:///system"
redisHost = %s
redisPort = 6379

[rimp]
repository = /opt/vm_repository
datastore = /var/lib/virt

[vlan]
ifconfigCmd = /sbin/ifconfig
vconfigCmd = /sbin/vconfig
brctlCmd = /usr/sbin/brctl
""" % anaconda.id.abiquo.abiquo_rs_ip)
            f.close()
    
    if anaconda.backend.isGroupSelected('abiquo-xen'):
        # replace default kernel entry
        f = open(anaconda.rootPath + '/boot/grub/menu.lst')
        buf = f.readlines()
        f.close()
        fw = open(anaconda.rootPath + '/boot/grub/menu.lst', 'w')
        for line in buf:
            fw.write(re.sub('\/xen.gz-2.6.18.*',
                            '/xen.gz-3.4.2',
                            line))
        fw.close()

        f = open(anaconda.rootPath + "/etc/abiquo-aim.ini", "w")
        f.write("""
# AIM configuration file

[server]
port = 8889

[monitor]
uri = "xen+unix:///"
redisHost = %s
redisPort = 6379

[rimp]
repository = /opt/vm_repository
datastore = /var/lib/virt

[vlan]
ifconfigCmd = /sbin/ifconfig
vconfigCmd = /sbin/vconfig
brctlCmd = /usr/sbin/brctl
""" % anaconda.id.abiquo.abiquo_rs_ip)
        f.close()
    f = open(anaconda.rootPath + '/etc/abiquo-installer', 'a')
    f.write('Installed Profiles: %s\n' %
            str(anaconda.id.abiquo.selectedGroups))
    f.close()
    
    if anaconda.backend.isGroupSelected('abiquo-virtualbox') and \
            os.path.exists(anaconda.rootPath + '/etc/sysconfig/modules/kvm.modules'):
                os.remove(anaconda.rootPath + '/etc/sysconfig/modules/kvm.modules')
