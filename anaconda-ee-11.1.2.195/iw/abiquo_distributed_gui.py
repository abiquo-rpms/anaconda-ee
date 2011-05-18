#
# abiquo_gui.py: Choose tasks for installation
#
# Copyright 2011 Abiquo
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

import gtk
import gtk.glade
import gui
from iw_gui import *

class AbiquoDistributedWindow(InstallWindow):
    def getNext(self):
        self.data.abiquo.selectedGroups += self.selected_tasks
        map(self.backend.selectGroup, self.selected_tasks)

    def _selectionChanged(self, btn):
        lbl = btn.get_label()
        if btn.get_active():
            if lbl == 'Abiquo Server':
                self.selected_tasks.append('abiquo-server')
            elif lbl == 'Abiquo Remote Services':
                self.selected_tasks.append('abiquo-remote-services')
            elif lbl == 'Abiquo V2V Services':
                self.selected_tasks.append('abiquo-v2v')
        else:
            if lbl == 'Abiquo Server':
                self.selected_tasks.remove('abiquo-server')
            elif lbl == 'Abiquo Remote Services':
                self.selected_tasks.remove('abiquo-remote-services')
            elif lbl == 'Abiquo V2V Services':
                self.selected_tasks.remove('abiquo-v2v')

        print "Selected tasks %s" % self.selected_tasks

    def getScreen (self, anaconda):
        self.anaconda = anaconda
        self.data = anaconda.id
        self.backend = anaconda.backend

        self.selected_tasks = ['abiquo-server']
        (self.xml, vbox) = gui.getGladeWidget("abiquo_distributed.glade", "settingsBox")
        for btn in ['abiquoServerRadio', 'abiquoRSRadio', 'abiquoV2VRadio']:
            self.xml.get_widget(btn).connect(
                    'toggled',
                    self._selectionChanged)
        return vbox
