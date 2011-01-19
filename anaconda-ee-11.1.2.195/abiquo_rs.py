#
# timezone.py - timezone install data
#
# Copyright 2001 Red Hat, Inc.
#
# This software may be freely redistributed under the terms of the GNU
# library public license.
#
# You should have received a copy of the GNU Library Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

import shutil
import iutil
import os
from flags import flags

import logging
log = logging.getLogger("anaconda")

def bool(val):
    if val: return "true"
    return "false"

class AbiquoRS:

    def write(self, instPath):
        # dont do this in test mode!
        if flags.test:
            return
        f = open(instPath + "/opt/abiquo/config/abiquo.properties", 'a')
        f.write("[remote-services]\n")
        f.write("abiquo.rabbitmq.username = %s\n" %
                self.abiquo_rabbitmq_username)
        f.write("abiquo.rabbitmq.password = %s\n" %
                self.abiquo_rabbitmq_password)
        f.write("abiquo.rabbitmq.host = %s\n" %
                self.abiquo_rabbitmq_host)
        f.write("abiquo.rabbitmq.port = %s\n" %
                self.abiquo_rabbitmq_port)
        f.write("abiquo.appliancemanager.localRepositoryPath = %s\n" %
                self.abiquo_appliancemanager_localRepositoryPath)
        f.write("abiquo.appliancemanager.repositoryLocation = %s\n" %
                self.abiquo_appliancemanager_repositoryLocation)
        f.write("abiquo.virtualfactory.hyperv.repositoryLocation = %s\n" %
                self.abiquo_virtualfactory_hyperv_repositoryLocation)
        f.write("abiquo.virtualfactory.xenserver.repositoryLocation = %s\n" %
                self.abiquo_virtualfactory_xenserver_repositoryLocation)
        f.write("abiquo.virtualfactory.vmware.repositoryLocation = %s\n" %
                self.abiquo_virtualfactory_vmware_repositoryLocation)
        f.write("abiquo.virtualfactory.storagelink.user = %s\n" %
                self.abiquo_virtualfactory_storagelink_user)
        f.write("abiquo.virtualfactory.storagelink.password = %s\n" %
                self.abiquo_virtualfactory_storagelink_password)
        f.write("abiquo.virtualfactory.storagelink.address = %s\n" %
                self.abiquo_virtualfactory_storagelink_address)
        f.write("abiquo.redis.port = %s\n" %
                self.abiquo_redis_port)
        f.write("abiquo.redis.host = %s\n" %
                self.abiquo_redis_host)
        f.close()
    
    def writeKS(self, f):
	f.write("abiquo-remote-services --nfsrepository=%s\n" %
                self.abiquo_nfs_repository)

    def __init__(self):
        self.abiquo_nfs_repository = 'localhost:/opt/vm_repository'
        self.ontap_user = 'root'
        self.ontap_password = ''
        self.ontap_server_ip = '127.0.0.1'
        self.abiquo_rabbitmq_username = 'guest'
        self.abiquo_rabbitmq_password = 'guest'
        self.abiquo_rabbitmq_host = '127.0.0.1'
        self.abiquo_rabbitmq_port = '5672'
        self.abiquo_appliancemanager_localRepositoryPath = '/opt/vm_repository/'
        self.abiquo_appliancemanager_repositoryLocation  = '127.0.0.1:/opt/vm_repository/'
        self.abiquo_virtualfactory_hyperv_repositoryLocation = '//127.0.0.1/vm_repository/'
        self.abiquo_virtualfactory_xenserver_repositoryLocation = '127.0.0.1:/opt/vm_repository/'
        self.abiquo_virtualfactory_vmware_repositoryLocation = '127.0.0.1:/opt/vm_repository/'
        self.abiquo_virtualfactory_storagelink_address = 'https://127.0.0.1:21605'
        self.abiquo_virtualfactory_storagelink_user = 'admin'
        self.abiquo_virtualfactory_storagelink_password = 'storagelink'
        self.abiquo_redis_host =  '127.0.0.1'
        self.abiquo_redis_port = '6379'
