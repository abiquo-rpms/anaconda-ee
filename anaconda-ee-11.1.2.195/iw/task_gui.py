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
            self.dispatch.skipStep("abiquo_ontap", skip = 1)
            self.dispatch.skipStep("abiquo_rs", skip = 1)
        
        if not ('abiquo-v2v' in selected_groups):
            self.dispatch.skipStep("abiquo_v2v", skip = 1)
        else:
            self.dispatch.skipStep("abiquo_v2v", skip = 0)

        if 'abiquo-ontap' in selected_groups:
            self.dispatch.skipStep("abiquo_ontap", skip = 0)
        
        if 'abiquo-remote-services' in selected_groups:
            self.dispatch.skipStep("abiquo_rs", skip = 0)

        if not ('abiquo-ontap' in selected_groups):
            log.info("netapp connector not selected, skip.")
            self.dispatch.skipStep("abiquo_ontap", skip = 1)

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
            self.dispatch.skipStep("abiquo_rs", skip = 1)
            self.dispatch.skipStep("abiquo_hv", skip = 1)
        
        if ('abiquo-remote-services' in selected_groups) and \
                ('abiquo-server' in selected_groups) and \
                ('abiquo-v2v' in selected_groups):
            self.dispatch.skipStep("abiquo_rs", skip = 1)
            self.dispatch.skipStep("abiquo_hv", skip = 1)

        if ('abiquo-nfs-repository' in selected_groups):
            self.dispatch.skipStep("abiquo_v2v", skip = 1)



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

    def _setupRepo(self, repo):
        try:
            self.backend.doRepoSetup(self.anaconda, repo.id, fatalerrors = False)
            log.info("added repository %s with with source URL %s" % (repo.name, repo.baseurl[0]))
        except yum.Errors.RepoError, e:
            self.intf.messageWindow(_("Error"),
                  _("Unable to read package metadata from repository.  "
                    "This may be due to a missing repodata directory.  "
                    "Please ensure that your repository has been "
                    "correctly generated.\n\n%s" %(e,)),
                                    type="ok", custom_icon="error")
            self.backend.ayum.repos.delete(repo.id)
            return False

        if not repo.groups_added:
            self.intf.messageWindow(_("Warning"),
                           _("Unable to find a group file for %s.  "
                             "This will make manual selection of packages "
                             "from the repository not work") %(repo.id,),
                                    type="warning")

        return True

    def _addRepo(self, *args):
        if not network.hasActiveNetDev():
            net = NetworkConfigurator(self.anaconda.id.network)
            ret = net.run()
            net.destroy()
            if ret == gtk.RESPONSE_CANCEL:
                return gtk.RESPONSE_CANCEL
        
        (dxml, dialog) = gui.getGladeWidget("addrepo.glade", "addRepoDialog")
        gui.addFrame(dialog)

        lbl = dxml.get_widget("descLabel")
        txt = lbl.get_text()
        lbl.set_text(txt %(productName,))
        
        dialog.show_all()

        while 1:
            rc = dialog.run()
            if rc == gtk.RESPONSE_CANCEL:
                break
        
            reponame = dxml.get_widget("nameEntry").get_text()
            reponame.strip()
            if len(reponame) == 0:
                self.intf.messageWindow(_("Invalid Repository Name"),
                                        _("You must provide a non-zero length "
                                          "repository name."))
                continue

            repourl = dxml.get_widget("urlEntry").get_text()
            repourl.strip()
            if (len(repourl) == 0 or not
                (repourl.startswith("http://") or
                 repourl.startswith("ftp://"))):
                self.intf.messageWindow(_("Invalid Repository URL"),
                                        _("You must provide an HTTP or FTP "
                                          "URL to a repository."))
                continue

            # FIXME: this is yum specific
            repo = AnacondaYumRepo(uri=repourl, repoid=reponame)
            repo.name = reponame
            repo.basecachedir = self.backend.ayum.conf.cachedir
            repo.enable()

            try:
                self.backend.ayum.repos.add(repo)
            except yum.Errors.DuplicateRepoError, e:
                self.intf.messageWindow(_("Error"),
                      _("The repository %s has already been added.  Please "
                        "choose a different repository name and "
                        "URL.") % reponame, type="ok", custom_icon="error")
                continue

            if not self._setupRepo(repo):
                continue

            s = self.xml.get_widget("repoList").get_model()
            s.append([repo.isEnabled(), repo.name, repo])
            self.repos[repo.name] = (repo.baseurl[0], None)

            break

        dialog.destroy()
        return rc

    def _taskToggled(self, data, row, store):
        i = store.get_iter(int(row))
        val = store.get_value(i, 0)
        store.set_value(i, 0, not val)

    def _repoToggled(self, data, row, store):
        i = store.get_iter(int(row))
        val = store.get_value(i, 0)

        if not val and not network.hasActiveNetDev():
            net = NetworkConfigurator(self.anaconda.id.network)
            ret = net.run()
            net.destroy()
            if ret == gtk.RESPONSE_CANCEL:
                return
        
        store.set_value(i, 0, not val)

    def _createTaskStore(self):
        store = gtk.ListStore(gobject.TYPE_BOOLEAN,
                              gobject.TYPE_STRING,
                              gobject.TYPE_PYOBJECT)
        tl = self.xml.get_widget("taskList")
        tl.set_model(store)

        cbr = gtk.CellRendererToggle()
        col = gtk.TreeViewColumn('', cbr, active = 0)
        cbr.connect("toggled", self._taskToggled, store)
        tl.append_column(col)

        col = gtk.TreeViewColumn('Text', gtk.CellRendererText(), text = 1)
        col.set_clickable(False)
        tl.append_column(col)

        for (txt, grps) in self.tasks:
            if not self.groupsExist(grps):
                continue
            store.append([self.groupsInstalled(grps), _(txt), grps])

        return len(store)

    def _createRepoStore(self):
        store = gtk.ListStore(gobject.TYPE_BOOLEAN,
                              gobject.TYPE_STRING,
                              gobject.TYPE_PYOBJECT)
        tl = self.xml.get_widget("repoList")
        tl.set_model(store)

        cbr = gtk.CellRendererToggle()
        col = gtk.TreeViewColumn('', cbr, active = 0)
        cbr.connect("toggled", self._repoToggled, store)
        tl.append_column(col)

        col = gtk.TreeViewColumn('Text', gtk.CellRendererText(), text = 1)
        col.set_clickable(False)
        tl.append_column(col)

        for (reponame, uri) in self.repos.items():
            repoid = reponame.replace(" ", "")
            if not self.backend.ayum.repos.repos.has_key(repoid):
                continue
            repo = self.backend.ayum.repos.repos[repoid]
            store.append([repo.isEnabled(), repo.name, repo])
        
            
    def getScreen (self, anaconda):
        self.intf = anaconda.intf
        self.dispatch = anaconda.dispatch
        self.backend = anaconda.backend
        self.anaconda = anaconda

        self.tasks = anaconda.id.instClass.tasks
        self.repos = anaconda.id.instClass.repos

        (self.xml, vbox) = gui.getGladeWidget("tasksel.glade", "taskBox")

        lbl = self.xml.get_widget("mainLabel")
        if anaconda.id.instClass.description:
            #lbl.set_text(_(anaconda.id.instClass.description))
            lbl.set_markup(_(anaconda.id.instClass.description))
        else:
            txt = lbl.get_text()
            lbl.set_text(txt %(productName,))

	#custom = not self.dispatch.stepInSkipList("group-selection")
        #if custom:
        #    self.xml.get_widget("customRadio").set_active(True)
        #else:
        #    self.xml.get_widget("customRadio").set_active(False)

        if self._createTaskStore() == 0:
            self.xml.get_widget("cbVBox").hide()
            self.xml.get_widget("mainLabel").hide()

        self._createRepoStore()
        if not anaconda.id.instClass.allowExtraRepos:
            vbox.remove(self.xml.get_widget("addRepoBox"))

        self.xml.get_widget("addRepoButton").connect("clicked", self._addRepo)

        return vbox
