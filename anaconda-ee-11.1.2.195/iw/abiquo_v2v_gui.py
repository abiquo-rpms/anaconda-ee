#
# abiquo_gui.py: Choose tasks for installation
#
# Copyright 2010 Abiquo
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

import gtk
import gtk.glade
import gobject
import gui
from iw_gui import *
from rhpl.translate import _, N_
from constants import productName

from netconfig_dialog import NetworkConfigurator
import network

from yuminstall import AnacondaYumRepo
import yum.Errors

import logging
log = logging.getLogger("anaconda")

class AbiquoV2VWindow(InstallWindow):
    def getNext(self):
        self.data.abiquo_rs.abiquo_nfs_repository = \
        self.xml.get_widget('abiquo_nfs_repository').get_text()
        self.data.abiquo_rs.abiquo_datacenter_id = self.xml.get_widget('datacenterId').get_text()
    
    def helpButtonClicked(self, data):
        log.info("helpButtonClicked")
        msg = (
        "<b>NFS Repository</b>\n"
        "The NFS URI where the Abiquo NFS repository is located\n"
        "i.e.\n"
        "my-nfs-server-ip:/opt/vm_repository\n"
        "\n"
        "<b>Datacenter ID</b>\n"
        "A unique identifier for this datacenter.\n"
        "If you are installing Remote Services in a separate server,\n"
        "make sure you use the same Datacenter ID when installing Remote Services.\n"
        "\n"
        )
        self.intf.messageWindow(_("<b>V2V Services Settings</b>"), msg, type="ok")

    def getScreen (self, anaconda):
        self.intf = anaconda.intf
        self.dispatch = anaconda.dispatch
        self.backend = anaconda.backend
        self.anaconda = anaconda
        self.data = anaconda.id

        (self.xml, vbox) = gui.getGladeWidget("abiquo_v2v.glade", "settingsBox")
        self.xml.get_widget('abiquo_nfs_repository').set_text(self.data.abiquo_rs.abiquo_nfs_repository)
        self.xml.get_widget('datacenterId').set_text(self.data.abiquo_rs.abiquo_datacenter_id)
        self.helpButton = self.xml.get_widget("helpButton")
        self.helpButton.connect("clicked", self.helpButtonClicked)
        return vbox
