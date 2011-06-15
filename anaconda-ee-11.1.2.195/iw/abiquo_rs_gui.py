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
import re
import socket

from netconfig_dialog import NetworkConfigurator
import network

from yuminstall import AnacondaYumRepo
import yum.Errors

import logging
log = logging.getLogger("anaconda")

import urlparse

class AbiquoRSWindow(InstallWindow):
    def getNext(self):
        nfsUrl = self.xml.get_widget('abiquo_nfs_repository').get_text()
        if re.search('(localhost|127\.0\.0\.1)', nfsUrl):
            self.intf.messageWindow(_("<b>NFS Repository Error</b>"),
                       _("<b>127.0.0.1 or localhost detected</b>\n\n"
                         "127.0.0.1 or localhost values are not allowed here. "
                         "Use an IP address reachable by other hosts "
                         "in your LAN."),
                            type="warning")
            raise gui.StayOnScreen

        serverIP = self.xml.get_widget('abiquo_server_ip').get_text()
        if re.search('(localhost|127\.0\.0\.1)', serverIP):
            self.intf.messageWindow(_("<b>Abiquo Server IP Error</b>"),
                       _("<b>127.0.0.1 or localhost detected</b>\n\n"
                         "127.0.0.1 or localhost values are not allowed here. "
                         "Use an IP address reachable by other hosts "
                         "in your LAN."),
                                type="warning")
            raise gui.StayOnScreen

        # validate the host
        host = nfsUrl.split(":")[0]
        try:
            network.sanityCheckIPString(host)
        except:
            if network.sanityCheckHostname(host) is not None:
                self.intf.messageWindow(_("<b>Invalid NFS URL</b>"),
                           _("NFS Repository URL is invalid."),
                                    type="warning")
                raise gui.StayOnScreen

        # validate the abiquo server IP
        try:
            socket.inet_aton(serverIP.strip())
        except socket.error:
            self.intf.messageWindow(_("<b>Abiquo Server IP Error</b>"),
                       _("<b>Invalid IP Address</b>\n\n"
                         "%s is not a valid IP Address" % serverIP),
                                type="warning")
            raise gui.StayOnScreen

        if not re.search('.+:\/.*', nfsUrl):
            self.intf.messageWindow(_("<b>NFS Repository Error</b>"),
                       _("<b>Invalid NFS URL</b>\n\n"
                         "%s is not a valid NFS URL" % nfsUrl),
                                type="warning")
            raise gui.StayOnScreen


        self.data.abiquo_rs.abiquo_nfs_repository = nfsUrl
        self.data.abiquo_rs.abiquo_rabbitmq_host = serverIP

    def getScreen (self, anaconda):
        self.intf = anaconda.intf
        self.dispatch = anaconda.dispatch
        self.backend = anaconda.backend
        self.anaconda = anaconda
        self.data = anaconda.id

        (self.xml, vbox) = gui.getGladeWidget("abiquo_rs.glade", "settingsBox")
        self.xml.get_widget('abiquo_nfs_repository').set_text(self.data.abiquo_rs.abiquo_nfs_repository)
        
        server_ip = self.data.abiquo_rs.abiquo_rabbitmq_host
        if server_ip == '127.0.0.1':
            server_ip = '<server-ip>'
        self.xml.get_widget('abiquo_server_ip').set_text(server_ip)
        return vbox
