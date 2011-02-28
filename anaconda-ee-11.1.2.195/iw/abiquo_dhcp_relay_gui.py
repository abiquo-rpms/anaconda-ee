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
import socket

import logging
log = logging.getLogger("anaconda")

class AbiquoDHCPRelayWindow(InstallWindow):
    def getNext(self):
        self.data.abiquo.abiquo_dhcprelay_vrange_1 = self.xml.get_widget('vrange_1').get_text()
        
        self.data.abiquo.abiquo_dhcprelay_vrange_2 = self.xml.get_widget('vrange_2').get_text()

        if int(self.data.abiquo.abiquo_dhcprelay_vrange_1) >= int(self.data.abiquo.abiquo_dhcprelay_vrange_2):
            self.intf.messageWindow(_("<b>VLAN Range Error</b>"),
                       _("<b>Invalid Range</b>\n\n"
                         "VLAN Range 1 is equal or greater than VLAN Range 2"),
                                type="warning")
            raise gui.StayOnScreen
            
        
        combo = self.xml.get_widget('management_if')
        iter = combo.get_active_iter()
        self.data.abiquo.abiquo_dhcprelay_management_if = combo.get_model().get_value(iter, 0)
        
        combo = self.xml.get_widget('service_if')
        iter = combo.get_active_iter()
        self.data.abiquo.abiquo_dhcprelay_service_if = combo.get_model().get_value(iter, 0)
        

        # Get RELAY Server IP
        self.data.abiquo.abiquo_dhcprelay_relay_ip = self.xml.get_widget('relay_ip').get_text()
        try:
            socket.inet_aton(self.data.abiquo.abiquo_dhcprelay_relay_ip.strip())
        except socket.error:
            self.intf.messageWindow(_("<b>IP Error</b>"),
                       _("<b>Invalid DHCP Relay IP Address</b>\n\n"
                         "%s is not a valid IP Address" % self.data.abiquo.abiquo_dhcprelay_relay_ip),
                                type="warning")
            raise gui.StayOnScreen

        # DHCP Server IP
        self.data.abiquo.abiquo_dhcprelay_dhcpd_ip = self.xml.get_widget('dhcpd_ip').get_text()
        try:
            socket.inet_aton(self.data.abiquo.abiquo_dhcprelay_dhcpd_ip.strip())
        except socket.error:
            self.intf.messageWindow(_("<b>IP Error</b>"),
                       _("<b>Invalid DHCP Server IP Address</b>\n\n"
                         "%s is not a valid IP Address" % self.data.abiquo.abiquo_dhcprelay_dhcpd_ip),
                                type="warning")
            raise gui.StayOnScreen

        self.data.abiquo.abiquo_dhcprelay_service_network = self.xml.get_widget('service_network').get_text()

    def getScreen (self, anaconda):
        self.intf = anaconda.intf
        #self.dispatch = anaconda.dispatch
        #self.backend = anaconda.backend
        self.anaconda = anaconda
        self.data = anaconda.id

        (self.xml, vbox) = gui.getGladeWidget("abiquo_dhcp_relay.glade", "settingsBox")
        #self.xml.get_widget('abiquo_nfs_repository').set_text(self.data.abiquo_rs.abiquo_nfs_repository)
        #self.xml.get_widget('abiquo_rs_ip').set_text(self.data.abiquo.abiquo_rs_ip)
        return vbox
