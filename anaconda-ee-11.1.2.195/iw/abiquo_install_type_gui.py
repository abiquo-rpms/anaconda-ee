#
# welcome_gui.py: gui welcome screen.
#
# Copyright 2000-2002 Red Hat, Inc.
#
# This software may be freely redistributed under the terms of the GNU
# library public license.
#
# You should have received a copy of the GNU Library Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

import gtk
import gui
from iw_gui import *
from rhpl.translate import _, N_

class AbiquoInstallTypeWindow (InstallWindow):		

    def getNext(self):
        ciab = self.xml.get_widget('ciabRadio')
        #advanced = self.xml.get_widget('ciabRadio')
        if ciab.get_active():
            if not self.intf.messageWindow("<b>Warning</b>",
                         "<b>This will wipe out your disk</b>\n\n"
                         "Are you sure?",
                         type="yesno", custom_icon="question"):
                raise gui.StayOnScreen
            self.anaconda.id.abiquo.install_type = 'ciab'
            self.dispatch.skipStep("tasksel", skip=1)
            self.dispatch.skipStep("partition", skip=1)
            self.dispatch.skipStep("parttype", skip=1)
            self.dispatch.skipStep("bootloader", skip=1)
            self.dispatch.skipStep("abiquo_rs", skip=1)
            self.dispatch.skipStep("abiquo_v2v", skip=1)
            self.dispatch.skipStep("abiquo_hv", skip=1)
            self.dispatch.skipStep("abiquo_distributed", skip=1)
            self.dispatch.skipStep("abiquo_dhcp_relay", skip=1)
        else:
            self.anaconda.id.abiquo.install_type = 'advanced'
            self.dispatch.skipStep("tasksel", skip=0)
            self.dispatch.skipStep("partition", skip=0)
            self.dispatch.skipStep("parttype", skip=0)
            self.dispatch.skipStep("bootloader", skip=0)
            self.dispatch.skipStep("abiquo_rs", skip=0)
            self.dispatch.skipStep("abiquo_v2v", skip=0)
            self.dispatch.skipStep("abiquo_hv", skip=0)
            self.dispatch.skipStep("abiquo_distributed", skip=0)
            self.dispatch.skipStep("abiquo_dhcp_relay", skip=0)

    # WelcomeWindow tag="wel"
    def getScreen (self, anaconda):
        self.anaconda = anaconda
        self.intf = anaconda.intf
        self.dispatch = anaconda.dispatch
        self.backend = anaconda.backend
        (self.xml, box) = gui.getGladeWidget("abiquo_install_type.glade", "hbox1")
        return box

