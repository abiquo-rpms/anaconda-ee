from installclass import BaseInstallClass
import rhpl
from rhpl.translate import N_,_
from constants import *
from flags import flags
import os
import iutil
import types
import re
try:
    import instnum
except ImportError:
    instnum = None

import logging
log = logging.getLogger("anaconda")

# custom installs are easy :-)
class InstallClass(BaseInstallClass):
    # name has underscore used for mnemonics, strip if you dont need it
    id = "rhel"
    name = N_("Abiquo Linux")
    _description = N_("""
<b>Select one (or multiple) %s components to install</b>

<b>Cloud in a Box:</b> Abiquo + Storage + Hypervisor in one box.
<b>Server:</b> Installs Abiquo core, the API, MySQL and the web client.
<b>Remote Services:</b> Installs the components required to manage a remote datacenter from Abiquo (V2V is also needed, but can be installed on its own server).
<b>V2V Conversion Services:</b> Conversion services required for the Abiquo V2V features. Can be installed standalone (for best performance) or with the Remote Services.
<b>Abiquo NFS Repository:</b> Local repository to store the virtual appliances.

<b>Abiquo KVM Cloud Node:</b> Installs a KVM Cloud Node.
<b>Abiquo Xen Cloud Node:</b> Installs a Xen Cloud Node.
<b>Abiquo VirtualBox Cloud Node:</b> Installs a VirtualBox 4.0 Cloud Node.

<b>LVM Storage Server:</b> Abiquo LVM based iSCSI storage server.
<b>NetApp Storage Connector:</b> NetApp connector to manage NetApp Storage Servers.
<b>Remote Repository:</b> Abiquo Remote Repository.
                     """)
    _descriptionFields = (productName,)
    sortPriority = 10000
    allowExtraRepos = False
    if 0: # not productName.startswith("Red Hat Enterprise"):
        hidden = 1

    tasks =  [
              (N_("Cloud in a Box"), ["cloud-in-a-box"]),
              (N_("LVM Storage Server"), ["abiquo-lvm-storage-server"]),
              (N_("NetApp Storage Connector"), ["abiquo-ontap"]),
              (N_("Abiquo Server"), ["abiquo-server"]),
              (N_("Abiquo V2V Conversion Services"), ["abiquo-v2v"]),
              (N_("Abiquo Remote Services"), ["abiquo-remote-services"]),
              (N_("Abiquo NFS Repository"), ["abiquo-nfs-repository"]),
              (N_("Abiquo KVM"), ["abiquo-kvm"]),
              (N_("Abiquo Xen"), ["abiquo-xen"]),
              (N_("Abiquo VirtualBox"), ["abiquo-virtualbox"]),
              (N_("Abiquo Remote Repository"), ["abiquo-remote-repository"])
              ]

    instkeyname = N_("Installation Number")
    instkeydesc = N_("Would you like to enter an Installation Number "
                     "(sometimes called Subscription Number) now? This feature "
                     "enables the installer to access any extra components "
                     "included with your subscription.  If you skip this step, "
                     "additional components can be installed manually later.\n\n"
                     "See http://www.redhat.com/InstNum/ for more information.")
    skipkeytext = N_("If you cannot locate the Installation Number, consult "
                     "http://www.redhat.com/InstNum/")

    def setInstallData(self, anaconda):
	BaseInstallClass.setInstallData(self, anaconda)
        BaseInstallClass.setDefaultPartitioning(self, anaconda.id.partitions,
                                                CLEARPART_TYPE_LINUX)

    def setGroupSelection(self, anaconda):
        grps = anaconda.backend.getDefaultGroups(anaconda)
        map(lambda x: anaconda.backend.selectGroup(x), grps)

    def setSteps(self, dispatch):
	BaseInstallClass.setSteps(self, dispatch);
	dispatch.skipStep("partition")
	dispatch.skipStep("regkey", skip = 1)        

    def postAction(self, anaconda, serial):
        f = open(anaconda.rootPath + "/etc/motd", "w")

        f.write("""

                  Mb            
                  Mb            
                  Mb            H@
      ..J++...J,  Mb ..JJJ..    .,    .......    ..,      ...   ...+JJ.
    .dMY=!?7HNMP`.MNMB"??7TMm. .Mb  .JrC???7wo,  ,Hr      dM. .JM9=!?7WN,
   JHD`      ?#P .M#:      .HN..Hb .wZ!     .zw!`,Hr      dM`.d#!     ``Mr
   MN:        MP` MP`      `J#\.Hb ?O:       .rc ,Hr      dM`,HF        W#
   dMp       .HP` MN,      .dM`.Hb `OO.     .J?:`,Mb     .dM`.MN.      .Mt
    ?MNJ....gMMP .MMNa.....HB! .Hb  `zro...J?WN&. 7Mm....dM%` .WNa....+M=
      `7TYY"^ "^  "^ ?TYYY=`    7=   ` ????!``?TY   ?TYY"^`     .?TY9"=`
   
   

   Abiquo Release 1.7.0

""")
        f.close()
        
        if anaconda.backend.isGroupSelected('cloud-in-a-box'):
            f = open(anaconda.rootPath + "/opt/abiquo/config/abiquo.properties", "a")
            f.write("abiquo.virtualfactory.kvm.fullVirt = false\n")
            f.close()

        if anaconda.backend.isGroupSelected('abiquo-nfs-repository'):
            f = open(anaconda.rootPath + "/etc/exports", "a")
            f.write("/opt/vm_repository    *(rw,no_root_squash,subtree_check,insecure)\n")
            f.close()
            iutil.execWithRedirect("/sbin/chkconfig",
                                    ['nfs', "on"],
                                    stdout="/dev/tty5", stderr="/dev/tty5",
                                    root=anaconda.rootPath)

        if anaconda.backend.isGroupSelected('abiquo-remote-services'):
            iutil.execWithRedirect("/sbin/chkconfig",
                                    ['dhcpd', "on"],
                                    stdout="/dev/tty5", stderr="/dev/tty5",
                                    root=anaconda.rootPath)
            if not anaconda.backend.isGroupSelected('abiquo-nfs-repository'):
                f = open(anaconda.rootPath + "/etc/fstab", "a")
                f.write("%s /opt/vm_repository  nfs defaults    0 0\n" %
                            anaconda.id.abiquo_rs.abiquo_nfs_repository )
                f.close()

        if anaconda.backend.isGroupSelected('abiquo-server') or \
                anaconda.backend.isGroupSelected('cloud-in-a-box'):
                    iutil.execWithRedirect("/sbin/chkconfig",
                                            ['rabbitmq-server', "on"],
                                            stdout="/dev/tty5", stderr="/dev/tty5",
                                            root=anaconda.rootPath)

        if anaconda.backend.isGroupSelected('abiquo-v2v'):
            if not anaconda.backend.isGroupSelected('abiquo-nfs-repository'):
                f = open(anaconda.rootPath + "/etc/fstab", "a")
                f.write("%s /opt/vm_repository  nfs defaults    0 0\n" %
                            anaconda.id.abiquo_rs.abiquo_nfs_repository )
                f.close()

        iutil.execWithRedirect("/sbin/chkconfig",
                                ['mysqld', "on"],
                                stdout="/dev/tty5", stderr="/dev/tty5",
                                root=anaconda.rootPath)
        if anaconda.backend.isGroupSelected('cloud-in-a-box') or \
                anaconda.backend.isGroupSelected('abiquo-lvm-storage-server'):
                    iutil.execWithRedirect("/sbin/chkconfig",
                                ['tgtd', "on"],
                                stdout="/dev/tty5", stderr="/dev/tty5",
                                root=anaconda.rootPath)

        if anaconda.backend.isGroupSelected('abiquo-lvm-storage-server'):
            iutil.execWithRedirect("/sbin/chkconfig",
                                    ['abiquo-lvmiscsi', "on"],
                                    stdout="/dev/tty5", stderr="/dev/tty5",
                                    root=anaconda.rootPath)

        if anaconda.backend.isGroupSelected('abiquo-ontap'):
            iutil.execWithRedirect("/sbin/chkconfig",
                                    ['abiquo-ontap', "on"],
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
                if not anaconda.backend.isGroupSelected('cloud-in-a-box'):
                    if not anaconda.backend.isGroupSelected('abiquo-nfs-repository'):
                        f = open(anaconda.rootPath + "/etc/fstab", "a")
                        f.write("%s /opt/vm_repository  nfs defaults    0 0\n" %
                            anaconda.id.abiquo_rs.abiquo_nfs_repository )
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

            
            if not anaconda.backend.isGroupSelected('cloud-in-a-box'):
                if not anaconda.backend.isGroupSelected('abiquo-nfs-repository'):
                    f = open(anaconda.rootPath + "/etc/fstab", "a")
                    f.write("%s /opt/vm_repository  nfs defaults    0 0\n" %
                        anaconda.id.abiquo_rs.abiquo_nfs_repository )
                    f.close()
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



    def handleRegKey(self, key, intf, interactive = True):
        self.repopaths = { "base": "%s" %(productPath,) }
        self.tasks = self.taskMap[productPath.lower()]
        self.installkey = key

        try:
            inum = instnum.InstNum(key)
        except Exception, e:
            if True or not BETANAG: # disable hack keys for non-beta
                # make sure the log is consistent
                log.info("repopaths is %s" %(self.repopaths,))
                raise
            else:
                inum = None

        if inum is not None:
            # make sure the base products match
            if inum.get_product_string().lower() != productPath.lower():
                raise ValueError, "Installation number incompatible with media"

            for name, path in inum.get_repos_dict().items():
                # virt is only supported on i386/x86_64.  so, let's nuke it
                # from our repo list on other arches unless you boot with
                # 'linux debug'
                if name.lower() == "virt" and ( \
                        rhpl.getArch() not in ("x86_64","i386","ia64")
                        and not flags.debug):
                    continue
                self.repopaths[name.lower()] = path
                log.info("Adding %s repo" % (name,))

        else:
            key = key.upper()
            # simple and stupid for now... if C is in the key, add Clustering
            # if V is in the key, add Virtualization. etc
            if key.find("C") != -1:
                self.repopaths["cluster"] = "Cluster"
                log.info("Adding Cluster option")
            if key.find("S") != -1:
                self.repopaths["clusterstorage"] = "ClusterStorage"
                log.info("Adding ClusterStorage option")
            if key.find("W") != -1:
                self.repopaths["workstation"] = "Workstation"
                log.info("Adding Workstation option")
            if key.find("V") != -1:
                self.repopaths["virt"] = "VT"
                log.info("Adding Virtualization option")

        for repo in self.repopaths.values():
            if not self.taskMap.has_key(repo.lower()):
                continue

            for task in self.taskMap[repo.lower()]:
                if task not in self.tasks:
                    self.tasks.append(task)
        self.tasks.sort()

        log.info("repopaths is %s" %(self.repopaths,))

    def __init__(self, expert):
	BaseInstallClass.__init__(self, expert)

        self.repopaths = { "base": "%s" %(productPath,) }

        # minimally set up tasks in case no key is provided
        #self.tasks = self.taskMap[productPath.lower()]

