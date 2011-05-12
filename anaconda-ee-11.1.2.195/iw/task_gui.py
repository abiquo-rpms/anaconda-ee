#
# task_gui.py: Choose tasks for installation
#
# Copyright 2006 Red Hat, Inc.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

import gtk
import gtk.glade
import gobject
import gui
import abiquo_groups
from iw_gui import *
from rhpl.translate import _, N_
from constants import productName

from netconfig_dialog import NetworkConfigurator
import network

from yuminstall import AnacondaYumRepo
import yum.Errors

import logging
log = logging.getLogger("anaconda")

class TaskWindow(InstallWindow):

    def getNext(self):
        tasks = self.xml.get_widget("selectedTasksList").get_model()
        selected_groups = []
        for (task, grps) in tasks:
            groups = []
            if type(grps) == str:
                groups = groups + [grps]
            else:
                groups = groups + grps

            map(self.backend.selectGroup, groups)
            selected_groups = selected_groups + groups 

        self.anaconda.id.abiquo.selectedGroups = selected_groups

        if 'cloud-in-a-box' in selected_groups:
            log.info("cloud-in-a-box selected, skip.")
            self.dispatch.skipStep("abiquo", skip = 1)
        
        if not ('abiquo-v2v' in selected_groups):
            self.dispatch.skipStep("abiquo_v2v", skip = 1)
        else:
            self.dispatch.skipStep("abiquo_v2v", skip = 0)

        if 'abiquo-remote-services' in selected_groups:
            self.dispatch.skipStep("abiquo_rs", skip = 0)

        if (not ('abiquo-server' in selected_groups)) and \
           (not ('cloud-in-a-box' in selected_groups)):
            log.info("abiquo-server not selected, skip.")
            self.dispatch.skipStep("abiquo", skip = 1)
        else:
            self.dispatch.skipStep("abiquo", skip = 0)
        
        if (not ('abiquo-remote-services' in selected_groups)) and \
           (not ('cloud-in-a-box' in selected_groups)):
            log.info("abiquo-remote-services not selected, skip.")
            self.dispatch.skipStep("abiquo_rs", skip = 1)
        else:
            self.dispatch.skipStep("abiquo_rs", skip = 0)
        
        if (('abiquo-xen' in selected_groups)) or \
           (('abiquo-kvm' in selected_groups)) or \
           (('abiquo-virtualbox' in selected_groups)):
            log.info("abiquo-kvm or abiquo-xen selected, show step.")
            self.dispatch.skipStep("abiquo_hv", skip = 0)
        else:
            log.info("abiquo-kvm/abiquo-xen/abiquo-virtualbox not selected, skip.")
            self.dispatch.skipStep("abiquo_hv", skip = 1)

        if ('cloud-in-a-box' in selected_groups):
            if 'abiquo-kvm' in selected_groups:
                self.intf.messageWindow(_("<b>Warning</b>"),
                           _("<b>Overlapping tasks selected</b>\n\n"
                             "You have selected Cloud in a Box install. "
                             "Selecting Abiquo KVM is not permitted. Please, "
                             "deselect Abiquo KVM and click next."),
                                    type="warning")
                raise gui.StayOnScreen
            
            if 'abiquo-virtualbox' in selected_groups:
                self.intf.messageWindow(_("<b>Warning</b>"),
                           _("<b>Overlapping tasks selected</b>\n\n"
                             "You have selected Cloud in a Box install. "
                             "Selecting Abiquo VirtualBox is not permitted. Please, "
                             "deselect Abiquo VirtualBox and click next."),
                                    type="warning")
                raise gui.StayOnScreen
            
            if 'abiquo-xen' in selected_groups:
                self.intf.messageWindow(_("<b>Warning</b>"),
                           _("<b>Overlapping tasks selected</b>\n\n"
                             "You have selected Cloud in a Box install. "
                             "Selecting Abiquo Xen is not permitted. Please, "
                             "deselect Abiquo Xen and click next."),
                                    type="warning")
                raise gui.StayOnScreen

            if 'abiquo-server' in selected_groups:
                self.intf.messageWindow(_("<b>Warning</b>"),
                           _("<b>Overlapping tasks selected</b>\n\n"
                             "You have selected Cloud in a Box install. "
                             "Selecting Abiquo Server is redundant. Please, "
                             "deselect Abiquo Server and click next."),
                                    type="warning")
                raise gui.StayOnScreen
            if 'abiquo-remote-services' in selected_groups:
                self.intf.messageWindow(_("<b>Warning</b>"),
                           _("<b>Overlapping tasks selected</b>\n\n"
                             "You have selected <i>Cloud in a Box</i> install. "
                             "Selecting Abiquo Remote Services is redundant. Please, "
                             "deselect Abiquo Remote Services and click next."),
                                    type="warning")
                raise gui.StayOnScreen
            if 'abiquo-v2v' in selected_groups:
                self.intf.messageWindow(_("<b>Warning</b>"),
                           _("<b>Overlapping tasks selected</b>\n\n"
                             "You have selected <i>Cloud in a Box</i> install. "
                             "Selecting Abiquo V2V is redundant. Please, "
                             "deselect Abiquo V2V and click next."),
                                    type="warning")
                raise gui.StayOnScreen

        if 'abiquo-kvm' in selected_groups:
            if ('abiquo-xen' in selected_groups) or \
                    ('abiquo-virtualbox' in selected_groups):
                self.intf.messageWindow(_("<b>Warning</b>"),
                           _("<b>Overlapping tasks selected</b>\n\n"
                             "You have selected <i>Abiquo KVM</i> install. "
                             "Selecting multiple hypervisor profiles is not allowed. Please, "
                             "select only one of VirtualBox/Xen/KVM and click next."),
                                    type="warning")
                raise gui.StayOnScreen
        
        if 'abiquo-virtualbox' in selected_groups:
            if ('abiquo-kvm' in selected_groups) or \
                    ('abiquo-xen' in selected_groups):
                self.intf.messageWindow(_("<b>Warning</b>"),
                           _("<b>Overlapping tasks selected</b>\n\n"
                             "You have selected <i>Abiquo VirtualBox</i> install. "
                             "Selecting multiple hypervisor profiles is not allowed. Please, "
                             "select only one of VirtualBox/Xen/KVM and click next."),
                                    type="warning")
                raise gui.StayOnScreen
        
        if ('cloud-in-a-box' in selected_groups) and \
                ('abiquo-nfs-repository' in selected_groups):
                    self.intf.messageWindow(_("<b>Warning</b>"),
                            _("<b>Overlapping tasks selected</b>\n\n"
                             "You have selected <i>Abiquo Cloud-in-a-Box</i> install. "
                             "Deselect Abiquo NFS Repository, it's not required."),
                            type="warning")
                    raise gui.StayOnScreen
        
        if 'abiquo-remote-repository' in selected_groups:
            if 'cloud-in-a-box' in selected_groups:
                self.intf.messageWindow(_("<b>Warning</b>"),
                           _("<b>Overlapping tasks selected</b>\n\n"
                             "You have selected <i>Abiquo Cloud-in-a-Box</i> install. "
                             "Selecting Abiquo Remote Repository is not allowed. Please, "
                             "deselect Abiquo Remote Repository and click next."),
                                    type="warning")
                raise gui.StayOnScreen
            
            if 'abiquo-server' in selected_groups:
                self.intf.messageWindow(_("<b>Warning</b>"),
                           _("<b>Overlapping tasks selected</b>\n\n"
                             "You have selected <i>Abiquo Server</i> install. "
                             "Selecting Abiquo Remote Repository is not allowed. Please, "
                             "deselect Abiquo Remote Repository and click next."),
                                    type="warning")
                raise gui.StayOnScreen
            
            if 'abiquo-remote-services' in selected_groups:
                self.intf.messageWindow(_("<b>Warning</b>"),
                           _("<b>Overlapping tasks selected</b>\n\n"
                             "You have selected <i>Abiquo Remote Services</i> install. "
                             "Selecting Abiquo Remote Repository is not allowed. Please, "
                             "deselect Abiquo Remote Repository and click next."),
                                    type="warning")
                raise gui.StayOnScreen
            
            if 'abiquo-v2v' in selected_groups:
                self.intf.messageWindow(_("<b>Warning</b>"),
                           _("<b>Overlapping tasks selected</b>\n\n"
                             "You have selected <i>Abiquo V2V Conversion Services</i> install. "
                             "Selecting Abiquo Remote Repository is not allowed. Please, "
                             "deselect Abiquo Remote Repository and click next."),
                                    type="warning")
                raise gui.StayOnScreen

        if 'cloud-in-a-box' in selected_groups:
            #self.dispatch.skipStep("abiquo_rs", skip = 1)
            self.dispatch.skipStep("abiquo_hv", skip = 1)
            self.dispatch.skipStep("abiquo_v2v", skip = 1)
        
        if ('abiquo-remote-services' in selected_groups) and \
                ('abiquo-server' in selected_groups) and \
                ('abiquo-v2v' in selected_groups):
            self.dispatch.skipStep("abiquo_rs", skip = 0)
            self.dispatch.skipStep("abiquo_hv", skip = 1)
            self.dispatch.skipStep("abiquo_v2v", skip = 1)

        if not ('abiquo-dhcp-relay' in selected_groups):
            self.dispatch.skipStep("abiquo_dhcp_relay", skip = 1)
        else:
            self.dispatch.skipStep("abiquo_dhcp_relay", skip = 0)
        
        if ('abiquo-dhcp-relay' in selected_groups) and \
                ('cloud-in-a-box' in selected_groups):
                    self.intf.messageWindow(_("<b>Warning</b>"),
                            _("<b>Overlapping tasks selected</b>\n\n"
                             "You have selected <i>Abiquo DHCP Relay</i> install. "
                             "Selecting Cloud-in-a-Box is not permitted."),
                            type="warning")
                    raise gui.StayOnScreen
        
        if ('abiquo-dhcp-relay' in selected_groups) and \
                ('abiquo-remote-services' in selected_groups):
                    self.intf.messageWindow(_("<b>Warning</b>"),
                            _("<b>Overlapping tasks selected</b>\n\n"
                             "You have selected <i>Abiquo DHCP Relay</i> install. "
                             "Selecting Remote Services is not permitted."),
                            type="warning")
                    raise gui.StayOnScreen



    def groupsInstalled(self, lst):
        # FIXME: yum specific
        rc = False
        for gid in lst:
            g = self.backend.ayum.comps.return_group(gid)
            if g and not g.selected:
                return False
            elif g:
                rc = True
        return rc

    def groupsExist(self, lst):
        # FIXME: yum specific
        for gid in lst:
            g = self.backend.ayum.comps.return_group(gid)
            if not g:
                return False
        return True
    
    def _task_store_sel_changed(self, tree_selection):
        lbl = self.xml.get_widget("taskDescLabel")
        model, iter = tree_selection.get_selected()
        selection = model.get_value(iter, 0)
        self.current_task = selection
        lbl.set_markup(abiquo_groups.group_descriptions[selection])
        subtasks = abiquo_groups.groups[selection]

        model = self.subtask_models[selection]
        tl = self.xml.get_widget("subtaskList")
        tl.set_model(model)
        if len(model) <= 0:
            for t in subtasks:
                self.subtask_models[selection].append([0,t])

    def _createTaskStore(self):
        store = gtk.ListStore(str)
        tl = self.xml.get_widget("taskList")
        tl.set_model(store)
        sel = tl.get_selection()
        sel.connect('changed', self._task_store_sel_changed)


        col = gtk.TreeViewColumn('Text', gtk.CellRendererText(), text = 0)
        col.set_clickable(False)
        tl.append_column(col)

        for k in abiquo_groups.groups:
            store.append([k])

    def _createSelectedTasksStore(self):
        store = gtk.ListStore(str, gobject.TYPE_PYOBJECT)
        tl = self.xml.get_widget("selectedTasksList")
        tl.set_model(store)

        col = gtk.TreeViewColumn('Selected Components', gtk.CellRendererText(), text = 0)
        col.set_clickable(False)
        tl.append_column(col)

    def _createSubgroupsDiag(self):
        list = self.diag1_xml.get_widget("subgroupList")
        store = gtk.ListStore(gobject.TYPE_BOOLEAN, str, gobject.TYPE_PYOBJECT)
        list.set_model(store)
        
        cbr = gtk.CellRendererToggle()
        col = gtk.TreeViewColumn('', cbr, active = 0)
        cbr.connect("toggled", self._subgroupToggled, 0)
        list.append_column(col)

        col = gtk.TreeViewColumn('Abiquo Platform Component', gtk.CellRendererText(), text = 1)
        col.set_clickable(False)
        list.append_column(col)

    def _presentSubgroups(self, groups):
        list = self.diag1_xml.get_widget("subgroupList")
        diag = self.diag1_xml.get_widget("dialog1")
        store = list.get_model()
        store.clear()
        for g in groups:
            store.append([0,g,g])
        res = diag.run()
        diag.hide()
        return res

    def _subgroupToggled(self, data, row, store):
        model = self.diag1_xml.get_widget("subgroupList").get_model()
        i = model.get_iter(int(row))
        val = model.get_value(i, 0)
        comp = model.get_value(i, 1)
        model.set_value(i, 0, not val)
        tl = self.xml.get_widget("selectedTasksList")
        stl_store = tl.get_model()
        found = 0
        for row in stl_store:
            if row[0] == comp:
                found = 1
                if val:
                    stl_store.remove(row.iter)

        if not found and not val:
            stl_store.append([comp, comp])

    def _checkValidSelection(self, sel):
        store = self.xml.get_widget("subtaskList").get_model()
        current = 0

        if sel in ["Distributed Install", "Cloud in a Box", "Monolithic Install",
                   "Abiquo KVM", "Abiquo Xen", "Abiquo VirtualBox"]:
            for row in store:
                if row[0]:
                    current = row[1]

            if not current:
                return 1
            elif current == sel:
                return 1
            else:
                return 0
        else:
            return 1

    def _taskToggled(self, data, row, store):
        model = self.subtask_models[self.current_task]
        i = model.get_iter(int(row))
        component = model.get_value(i, 1)
        if not self._checkValidSelection(component):
            return

        val = model.get_value(i, 0)
        model.set_value(i, 0, not val)
        tl = self.xml.get_widget("selectedTasksList")
        store = tl.get_model()
        if not val:
            # sub-groups available, present dialog
            if type(abiquo_groups.groups[self.current_task][component]) is list:
                res = self._presentSubgroups(abiquo_groups.groups[self.current_task][component])
                selections = 0
                for row in self.diag1_xml.get_widget("subgroupList").get_model():
                    if row[0]:
                        selections = 1
                if not selections:
                    model.set_value(i, 0, 0)
                    #store.append([component, abiquo_groups.groups[self.current_task]])
            else:
                store.append([component, abiquo_groups.groups[self.current_task][component]])
        else:
            if type(abiquo_groups.groups[self.current_task][component]) is list:
                for row in self.diag1_xml.get_widget("subgroupList").get_model():
                    for row2 in store:
                        if row2[0] == row[1]:
                            store.remove(row2.iter)

            iter = store.get_iter_first()
            while iter and store.iter_is_valid(iter):
                curr = store.get_value(iter, 0)
                if curr == component:
                    store.remove(iter)
                iter = store.iter_next(iter)

    def _createSubtaskStore(self):
        for k in abiquo_groups.groups:
            self.subtask_models[k] = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING)

        tl = self.xml.get_widget("subtaskList")
        cbr = gtk.CellRendererToggle()
        col = gtk.TreeViewColumn('', cbr, active = 0)
        cbr.connect("toggled", self._taskToggled, 0)
        tl.append_column(col)


        col = gtk.TreeViewColumn('Text', gtk.CellRendererText(), text = 1)
        col.set_clickable(False)
        tl.append_column(col)
    
    def getScreen (self, anaconda):
        self.intf = anaconda.intf
        self.dispatch = anaconda.dispatch
        self.backend = anaconda.backend
        self.anaconda = anaconda

        self.tasks = anaconda.id.instClass.tasks
        self.repos = anaconda.id.instClass.repos
        
        (self.xml, vbox) = gui.getGladeWidget("tasksel.glade", "vbox2")
        (self.diag1_xml, diag) = gui.getGladeWidget("tasksel.glade", "dialog1")

        lbl = self.xml.get_widget("mainLabel")
        self.subtask_models = {}
        self.current_task = 0
        self._createSubtaskStore()
        self._createTaskStore()
        self._createSelectedTasksStore()
        self._createSubgroupsDiag()

        return vbox
