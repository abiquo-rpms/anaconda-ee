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
from iw_gui import *
from rhpl.translate import _, N_
from constants import productName

from netconfig_dialog import NetworkConfigurator
import network

from yuminstall import AnacondaYumRepo
import yum.Errors

import logging
log = logging.getLogger("anaconda")

class AbiquoAdditionalTasks(gtk.TreeView):
    def __init__(self,anaconda):
        self.selected_tasks = []
        self.final_groups = anaconda.id.abiquo.selectedGroups
        gtk.TreeView.__init__(self)

        self._setupStore()
        cbr = gtk.CellRendererToggle()
        col = gtk.TreeViewColumn('', cbr, active = 0)
        cbr.connect("toggled", self._taskToggled)
        self.append_column(col)

        col = gtk.TreeViewColumn('Abiquo Additional Components', gtk.CellRendererText(), text = 1)
        col.set_clickable(False)
        self.append_column(col)

    def _setupStore(self):
        self.store = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.store.append([('abiquo-remote-repository' in self.final_groups), "Abiquo Remote Repository", 'abiquo-remote-repository'])
        self.store.append([('abiquo-dhcp-relay' in self.final_groups), "Abiquo DCHP Relay", 'abiquo-dhcp-relay'])
        self.store.append([('abiquo-nfs-repository' in self.final_groups), "Abiquo NFS Repository", 'abiquo-nfs-repository'])
        self.set_model(self.store)

        for g in ['abiquo-nfs-repository', 'abiquo-remote-repository', 'abiquo-dhcp-relay']:
            if (g in self.final_groups):
                self.selected_tasks.append(g)


    def _taskToggled(self, path, row):
        i = self.store.get_iter(int(row))
        val = self.store.get_value(i, 0)
        self.store.set_value(i, 0, not val)
        comp = self.store.get_value(i, 2)
        if not val:
            self.selected_tasks.append(comp)
        else:
            self.selected_tasks.remove(comp)

class AbiquoPlatformTasks(gtk.TreeView):
    def __init__(self, anaconda):
        self.final_groups = anaconda.id.abiquo.selectedGroups
        self.selected_task = 'none'
        gtk.TreeView.__init__(self)

        self._setupStore()
        cbr = gtk.CellRendererToggle()
        cbr.set_radio(True)
        col = gtk.TreeViewColumn('', cbr, active = 0)
        cbr.connect("toggled", self._taskToggled)
        self.get_selection().connect('changed', self._selectionChanged)

        self.append_column(col)

        col = gtk.TreeViewColumn('Available Components', gtk.CellRendererText(), text = 1)
        col.set_clickable(False)
        self.append_column(col)

    def _setupStore(self):
        self.store = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_STRING)

        # Check if no abiquo groups have been selected
        sel = True
        for g in ['abiquo-server', 'abiquo-remote-services', 'abiquo-v2v', 'cloud-in-a-box', 'abiquo-monolithic']:
            if g in self.final_groups:
                sel = False
        self.store.append([sel, "None", 'none'])

        # check if cloud-in-a-box previously selected
        self.store.append([('cloud-in-a-box' in self.final_groups), "Cloud in a Box Install", 'cloud-in-a-box'])

        # check if monolithic previously selected
        self.store.append([('abiquo-monolithic' in self.final_groups), "Monolithic Install", 'abiquo-monolithic'])

        # check if distributed previously selected
        sel = False
        for g in ['abiquo-server', 'abiquo-remote-services', 'abiquo-v2v']:
            if g in self.final_groups:
                sel = True
        self.store.append([sel, "Distributed Install", 'abiquo-distributed'])
        self.set_model(self.store)


    def _selectionChanged(self, selection):
        #selection = self.store.get_value(iter, 1)
        model, iter = selection.get_selected()
        sel = self.store.get_value(iter, 2)

    def _taskToggled(self, path, row):
        i = self.store.get_iter(int(row))
        for row in self.store:
            row[0] = False
            
        val = self.store.get_value(i, 0)
        self.store.set_value(i, 0, not val)
        comp = self.store.get_value(i, 2)
        self.selected_task = comp
        print self.selected_task

class AbiquoHypervisorTasks(AbiquoPlatformTasks):

    def __init__(self, anaconda):
        self.final_groups = anaconda.id.abiquo.selectedGroups
        AbiquoPlatformTasks.__init__(self, anaconda)
    
    def _setupStore(self):
        self.store = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_STRING)
        
        sel = True
        for g in ['abiquo-kvm', 'abiquo-xen', 'abiquo-virtualbox']:
            if g in self.final_groups:
                sel = False
        self.store.append([sel, "None", 'none'])
        self.store.append([('abiquo-kvm' in self.final_groups), "KVM Cloud Node", 'abiquo-kvm'])
        self.store.append([('abiquo-xen' in self.final_groups), "Xen Cloud Node", 'abiquo-xen'])
        self.store.append([('abiquo-virtualbox' in self.final_groups), "VirtualBox Cloud Node", 'abiquo-virtualbox'])
        self.set_model(self.store)

class OpscodeTasks(AbiquoPlatformTasks):

    def __init__(self, anaconda):
        self.final_groups = anaconda.id.abiquo.selectedGroups
        AbiquoPlatformTasks.__init__(self, anaconda)
    
    def _setupStore(self):
        self.store = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_STRING)
        
        sel = True
        for g in ['opschef-server', 'opschef-client']:
            if g in self.final_groups:
                sel = False
        self.store.append([sel, "None", 'none'])
        self.store.append([('opschef-server' in self.final_groups), "Opscode Chef Server", 'opschef-server'])
        self.store.append([('opschef-client' in self.final_groups), "Opscode Chef Client", 'opschef-client'])
        self.set_model(self.store)

class AbiquoStorageTasks(AbiquoPlatformTasks):

    def __init__(self, anaconda):
        self.final_groups = anaconda.id.abiquo.selectedGroups
        AbiquoPlatformTasks.__init__(self, anaconda)
    
    def _setupStore(self):
        self.store = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.store.append([('abiquo-lvmiscsi' not in self.final_groups), "None", 'none'])
        self.store.append([('abiquo-lvmiscsi' in self.final_groups), "Abiquo LVM Server", 'abiquo-lvmiscsi'])
        self.set_model(self.store)

class TaskWindow(InstallWindow):

    def getNext(self):
        selected_groups = []

        t = self.abiquo_storage_tasks.selected_task
        if t != 'none':
            selected_groups.append(t)
        t = self.opscode_tasks.selected_task
        if t != 'none':
            selected_groups.append(self.opscode_tasks.selected_task)
        t = self.abiquo_hypervisor_tasks.selected_task
        if t != 'none':
            selected_groups.append(self.abiquo_hypervisor_tasks.selected_task)
        
        t = self.abiquo_platform_tasks.selected_task
        if t != 'none':
            selected_groups.append(self.abiquo_platform_tasks.selected_task)
        
        t = self.abiquo_additional_tasks.selected_tasks
        if len(t) > 0:
            selected_groups = selected_groups + self.abiquo_additional_tasks.selected_tasks
        
        self.anaconda.id.abiquo.selectedGroups = selected_groups
        for g in self.abiquo_groups:
            if g in selected_groups:
                map(self.backend.selectGroup, [g])
            else:
                map(self.backend.deselectGroup, [g])

        if 'abiquo-distributed' not in selected_groups:
            self.dispatch.skipStep("abiquo_distributed", skip = 1)

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
        w = self.xml.get_widget("subtaskSW")
        if w.get_child():
            w.remove(w.get_child())
        if selection == "Abiquo Platform":
            w.add(self.abiquo_platform_tasks)
            self.abiquo_platform_tasks.show()
        elif selection == "Cloud Nodes":
            w.add(self.abiquo_hypervisor_tasks)
            self.abiquo_hypervisor_tasks.show()
        elif selection == "Opscode Chef":
            w.add(self.opscode_tasks)
            self.opscode_tasks.show()
        elif selection == "Storage Plugins":
            w.add(self.abiquo_storage_tasks)
            self.abiquo_storage_tasks.show()
        elif selection == "Additional Components":
            w.add(self.abiquo_additional_tasks)
            self.abiquo_additional_tasks.show()
        else:
            pass

        lbl.set_markup(self.tasks_descriptions[selection])


    def _createTaskStore(self):
        store = gtk.ListStore(str)
        tl = self.xml.get_widget("taskList")
        tl.set_model(store)
        sel = tl.get_selection()
        sel.connect('changed', self._task_store_sel_changed)


        col = gtk.TreeViewColumn('Text', gtk.CellRendererText(), text = 0)
        col.set_clickable(False)
        tl.append_column(col)

        for k in self.installer_tasks:
            store.append([k])

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

    def getScreen (self, anaconda):
        self.intf = anaconda.intf
        self.dispatch = anaconda.dispatch
        self.backend = anaconda.backend
        self.anaconda = anaconda
        self.abiquo_groups = ['cloud-in-a-box', 'abiquo-monolithic',
                  'abiquo-server', 'abiquo-remote-services', 'abiquo-v2v',
                  'opschef-server','opschef-client',
                  'abiquo-kvm', 'abiquo-xen', 'abiquo-virtualbox',
                  'abiquo-dhcp-relay', 'abiquo-nfs-repository',
                  'abiquo-remote-repository'
                  ]

        self.tasks = anaconda.id.instClass.tasks
        self.repos = anaconda.id.instClass.repos
        
        (self.xml, vbox) = gui.getGladeWidget("tasksel.glade", "mainWidget")
        (self.diag1_xml, diag) = gui.getGladeWidget("tasksel.glade", "dialog1")

        lbl = self.xml.get_widget("mainLabel")

        self.installer_tasks = ["Abiquo Platform", "Cloud Nodes", "Storage Plugins", "Opscode Chef", "Additional Components"]
        self.tasks_descriptions = {
            "Cloud Nodes": "<b>Cloud Nodes</b>\nInstall Abiquo KVM, Xen or VirtualBox Cloud Nodes (OpenSource hypervisors tested and supported by Abiquo).",
            "Opscode Chef": "<b>Chef</b>\nInstall Chef Server/Client components",
            "Abiquo Platform": "<b>Abiquo Platform</b>\nInstall selected Abiquo platform components to create a monolithic, distributed or cloud-in-a-box Abiquo installation.",
            "Storage Plugins": "<b>Storage Plugins</b>\nInstall required plugins to manage external storage such as a Linux LVM storage server.",
            "Additional Components": "<b>Additional Components</b>\nAbiquo Remote Repository, NFS Repository, etc.",
        }

        self._createTaskStore()
        self.abiquo_platform_tasks = AbiquoPlatformTasks(anaconda)
        self.abiquo_hypervisor_tasks = AbiquoHypervisorTasks(anaconda)
        self.opscode_tasks = OpscodeTasks(anaconda)
        self.abiquo_storage_tasks = AbiquoStorageTasks(anaconda)
        self.abiquo_additional_tasks = AbiquoAdditionalTasks(anaconda)
        return vbox

