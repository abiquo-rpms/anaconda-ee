#
# userauth_text.py: text mode authentication setup dialogs
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

from snack import *
from constants_text import *
from rhpl.translate import _

class AbiquoRSWindow:
    def __call__ (self, screen, anaconda):
        nfs_repository = anaconda.id.abiquo_rs.abiquo_nfs_repository 
        abiquo_server_ip = anaconda.id.abiquo_rs.abiquo_rabbitmq_host
        toplevel = GridFormHelp (screen, "Abiquo Remote Services Configuration",
                "abiquo_rs", 1, 4)
        toplevel.add (TextboxReflowed(37, "Abiquo NFS Repository URI. "
				"The NFS host and path where the Abiquo VM "
                                "Repository is located. "), 0, 0, (0, 0, 0, 1))

        entry1 = Entry (20, password = 0, text = nfs_repository)
        nfsgrid = Grid (2, 2)
        nfsgrid.setField (Label (_("NFS Repository:")), 0, 0, (0, 0, 1, 0), anchorLeft = 1)
        nfsgrid.setField (entry1, 1, 0)
        toplevel.add (nfsgrid, 0, 1, (0, 0, 0, 1))
        
        entry2 = Entry (20, password = 0, text = abiquo_server_ip)
        rsipgrid = Grid (2, 2)
        rsipgrid.setField (Label (_("Abiquo Server IP:")), 0, 0, (0, 0, 1, 0), anchorLeft = 1)
        rsipgrid.setField (entry1, 1, 0)
        toplevel.add (rsipgrid, 0, 1, (0, 0, 0, 1))

        bb = ButtonBar (screen, (TEXT_OK_BUTTON, TEXT_BACK_BUTTON))
        toplevel.add (bb, 0, 2, growx = 1)

        toplevel.setCurrent (entry1)
        result = toplevel.run ()
        rc = bb.buttonPressed (result)
        if rc == TEXT_BACK_CHECK:
            screen.popWindow()
	    return INSTALL_BACK

        anaconda.id.abiquo_rs.abiquo_nfs_repository = entry1.value()
        anaconda.id.abiquo_rs.abiquo_rabbitmq_host = entry2.value()
        screen.popWindow()
        return INSTALL_OK
