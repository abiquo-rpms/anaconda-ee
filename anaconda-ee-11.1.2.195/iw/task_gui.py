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

class TaskWindow(InstallWindow):

    def getNext(self):
        tasks = self.xml.get_widget("taskList").get_model()
        selected_groups = []
        for (cb, task, grps) in tasks:
            if cb:
                map(self.backend.selectGroup, grps)
                selected_groups = selected_groups + grps
                log.info('ABIQUO: selected groups %s' % grps)
                log.info('ABIQUO: selected groups class %s' % grps.__class__)
            else:
                map(self.backend.deselectGroup, grps)

        self.anaconda.id.abiquo.selectedGroups = selected_groups
        if self.anaconda.id.instClass.allowExtraRepos:
            repos = self.xml.get_widget("repoList").get_model()
            for (cb, reponame, repo) in repos:
                if cb:
                    repo.enable()

                    # Setup any repositories that were in the installclass's
                    # default list.
                    if not repo.ready():
                        self._setupRepo(repo)
                else:
                    repo.disable()

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
        lbl.set_markup(self.task_dsc_map[selection])
        subtasks = self.task_map[selection]

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
        
        for k in self.task_map:
            store.append([k])


    def _createSelectedTasksStore(self):
        store = gtk.ListStore(str, gobject.TYPE_PYOBJECT)

        tl = self.xml.get_widget("selectedTasksList")
        tl.set_model(store)

        col = gtk.TreeViewColumn('Selected Components', gtk.CellRendererText(), text = 0)
        col.set_clickable(False)
        tl.append_column(col)


    def _taskToggled(self, data, row, store):
        model = self.subtask_models[self.current_task]
        i = model.get_iter(int(row))
        val = model.get_value(i, 0)
        model.set_value(i, 0, not val)
        tl = self.xml.get_widget("selectedTasksList")
        store = tl.get_model()
        component = model.get_value(i, 1)
        if not val:
            store.append([component, self.pkg_group_map[component]])
        else:
            iter = store.get_iter_first()
            while iter and store.iter_is_valid(iter):
                curr = store.get_value(iter, 0)
                if curr == component:
                    store.remove(iter)
                iter = store.iter_next(iter)

    def _createSubtaskStore(self):
        for k in self.task_map:
            self.subtask_models[k] = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING)

        #self.subtask_store = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING)
        tl = self.xml.get_widget("subtaskList")
        #tl.set_model(self.subtask_store)

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
        
        self.task_map = {
                "Cloud Nodes": [ "Abiquo KVM", "Abiquo Xen", "Abiquo VirtualBox" ],
                "Distributed Install": [ "Abiquo Server", "Abiquo Remote Services", "Abiquo V2V" ],
                "Monolithic Install": ["Server + Remote Services + V2V"],
                "Storage Plugins": ["LVM Storage"],
                "Additional Components": ["Remote Repository", "NFS Repository","DHCP Relay"],
                "Opscode Chef": ["Chef Server", "Chef Client"],
                "Cloud in a Box": ["Cloud in a Box"],
                }

        self.task_dsc_map = {
                "Cloud Nodes": "<b>Cloud Nodes</b>\nInstall Abiquo KVM or Xen (compute) nodes.",
                "Opscode Chef": "<b>Chef</b>\nInstall Chef Server/Client components",
                "Distributed Install": "<b>Distributed Install</b>\nInstall selected Abiquo platform components to create a distributed Abiquo installation.",
                "Monolithic Install": "<b>Monolithic Install</b>\nInstall all the Abiquo platform components in one physical server.",
                "Storage Plugins": "<b>Storage Plugins</b>\nInstall required plugins to manage external storage such as a Linux LVM storage server.",
                "Additional Components": "<b>Additional Components</b>\nAbiquo Remote Repository, NFS Repository, etc.",
                "Cloud in a Box": "<b>Additional Components</b>\nInstalls Abiquo plus a KVM Cloud Node plus the LVM Storage Server. This installation type is not recommended for production environments.",
        }
        self.pkg_group_map = {
                "Abiquo KVM": ["abiquo-kvm"],
                "Abiquo Server": ["abiquo-server"],
                "Abiquo Remote Services": ["abiquo-remote-services"],
                "Abiquo V2V": ["abiquo-v2v"],
                "DHCP Relay": ["abiquo-dhcp-relay"],
                "Opscode Chef": ['chef-server', 'chef-client'],
                "Abiquo Xen": ['abiquo-xen'],
                "Abiquo VirtualBox":["abiquo-virtualbox"],
                "Server + Remote Services + V2V": ["abiquo-v2v", "abiquo-server", "abiquo-remote-services"],
                "LVM Storage": ['abiquo-lvm-storage-server'],
                "Remote Repository":["abiquo-remote-repository"],
                "NFS Repository": ["abiquo-nfs-repository"],
                "Cloud in a Box": ["cloud-in-a-box"],
                "Chef Server": ["chef-server"],
                "Chef Client": ["chef-client"],
        }


        (self.xml, vbox) = gui.getGladeWidget("tasksel.glade", "vbox2")

        lbl = self.xml.get_widget("mainLabel")
        self.subtask_models = {}
        self.current_task = 0
        self._createSubtaskStore()
        self._createTaskStore()
        self._createSelectedTasksStore()

        return vbox
