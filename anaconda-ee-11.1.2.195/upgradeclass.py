# this is the prototypical class for upgrades
#
# Copyright 2001-2004 Red Hat, Inc.
#
# This software may be freely redistributed under the terms of the GNU
# library public license.
#
# You should have received a copy of the GNU Library Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
from installclass import getBaseInstallClass
from rhpl.translate import N_, _

import os
import iutil
import rhpl

baseclass = getBaseInstallClass()

class InstallClass(baseclass):
    name = N_("Upgrade Existing System")
    pixmap = "upgrade.png"
    sortPriority = 999999

    parentClass = ( _("Upgrade"), "upgrade.png" )

    def requiredDisplayMode(self):
        return 't'

    def setSteps(self, dispatch):
	dispatch.setStepList(
		    "language",
		    "keyboard",
		    "welcome",
		    "installtype",
                    "findrootparts",
		    "findinstall",
                    "partitionobjinit",
                    "upgrademount",
                    "upgrademigfind",
                    "upgrademigratefs",
                    "upgradecontinue",
                    "reposetup",
                    "upgbootloader",
                    "checkdeps",
		    "dependencies",
		    "confirmupgrade",
                    "postselection",
		    "install",
                    "migratefilesystems",
                    "preinstallconfig",
                    "installpackages",
                    "postinstallconfig",
                    "instbootloader",
                    "dopostaction",
                    "writeregkey",
                    "methodcomplete",
                    "copylogs",
		    "complete"
		)

        if rhpl.getArch() != "i386" and rhpl.getArch() != "x86_64":
            dispatch.skipStep("bootloader")
            dispatch.skipStep("bootloaderadvanced")

        if rhpl.getArch() != "i386" and rhpl.getArch() != "x86_64":
            dispatch.skipStep("upgbootloader")            

    def setInstallData(self, anaconda):
        baseclass.setInstallData(self, anaconda)
        anaconda.id.setUpgrade(True)

    def postAction(self, anaconda, serial):
        upgrade_168_to_17_post(anaconda)
    
    def __init__(self, expert):
	baseclass.__init__(self, expert)

def upgrade_168_to_17_post(anaconda):
    # write MOTD
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

    #
    # Disable abiquo-tomcat service so we can run upgrade scripts safely
    # the first time the system starts after the upgrade
    #
    #if os.path.exists(anaconda.rootPath + '/etc/init.d/abiquo-tomcat'):
    #    iutil.execWithRedirect("/sbin/chkconfig",
    #                            ['abiquo-tomcat', "off"],
    #                            stdout="/dev/tty5", stderr="/dev/tty5",
    #                            root=anaconda.rootPath)
    #
    # make sure rabbitmq-server is started in the Abiquo Server box
    #
    if os.path.exists(anaconda.rootPath + '/etc/init.d/rabbitmq-server'):
        iutil.execWithRedirect("/sbin/chkconfig",
                                ['rabbitmq-server', "on"],
                                stdout="/dev/tty5", stderr="/dev/tty5",
                                root=anaconda.rootPath)

    #
    # Write the new (1.7) properties file in the RS and Server box
    # 
    if os.path.exists(anaconda.rootPath + '/opt/abiquo/backup/1.6.8/configs/virtualfactory.xml') or \
            os.path.exists(anaconda.rootPath + '/opt/abiquo/backup/1.6.8/configs/server.xml'):
        os.putenv('ABIQUO_CONFIG_HOME', '/opt/abiquo/backup/1.6.8/configs/')
        os.putenv('ABIQUO_PROPERTIES', '/opt/abiquo/config/abiquo.properties')
        iutil.execWithRedirect("/usr/bin/abiquo17-update-config", [''],
                                stdout="/dev/tty5", stderr="/dev/tty5",
                                root=anaconda.rootPath)
        f = open(anaconda.rootPath + "/opt/abiquo/config/.needsupgrade", "w")
        f.write("17-nuclear-launch\n")
        f.close()
