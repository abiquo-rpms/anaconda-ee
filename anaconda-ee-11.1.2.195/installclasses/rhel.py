from installclass import BaseInstallClass
import rhpl
from rhpl.translate import N_,_
from constants import *
from flags import flags
import os
import iutil
import types
import re
import shutil
from abiquo_postinstall_175 import *

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
<b>Select one (or multiple) %s components to install:</b>""")

#<b>Cloud in a Box:</b> Abiquo + Storage + Hypervisor in one box.
#<b>Server:</b> Installs Abiquo core, the API, MySQL and the web client.
#<b>Remote Services:</b> Installs the components required to manage a remote datacenter from Abiquo (V2V is also needed, but can be installed on its own server).
#<b>V2V Conversion Services:</b> Conversion services required for the Abiquo V2V features. Can be installed standalone (for best performance) or with the Remote Services.
#<b>Abiquo NFS Repository:</b> Local repository to store the virtual appliances.
#<b>Abiquo DHCP Relay:</b> DHCP Relay used to scale Abiquo multi-rack installations.
#
#<b>Abiquo KVM Cloud Node:</b> Installs a KVM Cloud Node.
#<b>Abiquo Xen Cloud Node:</b> Installs a Xen Cloud Node.
#<b>Abiquo VirtualBox Cloud Node:</b> Installs a VirtualBox 4.0 Cloud Node.
#
#<b>LVM Storage Server:</b> Abiquo LVM based iSCSI storage server.
#<b>Remote Repository:</b> Abiquo Remote Repository.
#                     """)
    _descriptionFields = (productName,)
    sortPriority = 10000
    allowExtraRepos = False
    if 0: # not productName.startswith("Red Hat Enterprise"):
        hidden = 1

    tasks =  [
              (N_("Cloud in a Box"), ["cloud-in-a-box"]),
              (N_("LVM Storage Server"), ["abiquo-lvm-storage-server"]),
              (N_("Abiquo Server"), ["abiquo-server"]),
              (N_("Abiquo V2V Conversion Services"), ["abiquo-v2v"]),
              (N_("Abiquo Remote Services"), ["abiquo-remote-services"]),
              (N_("Abiquo NFS Repository"), ["abiquo-nfs-repository"]),
              (N_("Abiquo KVM"), ["abiquo-kvm"]),
              (N_("Abiquo Xen"), ["abiquo-xen"]),
              (N_("Abiquo VirtualBox"), ["abiquo-virtualbox"]),
              (N_("Abiquo DHCP Relay"), ["abiquo-dhcp-relay"]),
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
        if anaconda.id.abiquo.install_type == 'ciab':
            map(anaconda.backend.selectGroup, ['cloud-in-a-box'])
            anaconda.id.abiquo.selectedGroups = ['cloud-in-a-box']
        else:
            map(anaconda.backend.deselectGroup, ['cloud-in-a-box'])

    def setSteps(self, dispatch):
	BaseInstallClass.setSteps(self, dispatch);
	dispatch.skipStep("partition")
	dispatch.skipStep("regkey", skip = 1)        

    def postAction(self, anaconda, serial):
        abiquoPostInstall(anaconda)

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

