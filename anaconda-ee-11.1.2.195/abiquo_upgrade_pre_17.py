import isys
import shutil
import glob
import os
import iutil
import time
import sys
import os.path

def abiquo_upgrade_pre(anaconda):
    backup_dir = anaconda.rootPath + '/opt/abiquo/backup/1.6.8' 
    if os.path.exists(backup_dir):
        anaconda.intf.messageWindow("Upgrade not possible",
                                    "Previous upgrade directory found. Aborting.")
	sys.exit(0)

    win = anaconda.intf.progressWindow("Upgrading",
                              "Nuclear Launch detected, upgrading to 1.7...", 
                              5)
    abiquo_config_dir = anaconda.rootPath + '/opt/abiquo/config'
    db_dir = anaconda.rootPath + '/var/lib/mysql/kinton'
    db_backup_dir = "%s/database/" % backup_dir
    old_16_configs_dir = "%s/configs" % backup_dir
    sysconfig_dir = anaconda.rootPath + "/etc/sysconfig"
    redis_db_file = anaconda.rootPath + '/var/lib/redis/dump.rdb'
    redis_backup_dir = backup_dir + "/redis"
    abiquo_ontap_dir = anaconda.rootPath + '/opt/abiquo/ontap'

    # Backup config files
    if os.path.exists(abiquo_config_dir) and \
            glob.glob(abiquo_config_dir + '/*.xml') > 0:
        if not os.path.exists(old_16_configs_dir):
            os.makedirs(old_16_configs_dir)
            for file in glob.glob(abiquo_config_dir + '/*.xml'):
                shutil.copy(file, old_16_configs_dir)
    # Remove old sysconfig abiquo files
    for file in glob.glob(sysconfig_dir + '/abiquo*'):
        os.remove(file)

    # Backup kinton database
    if os.path.isdir(db_dir):
        os.makedirs(db_backup_dir)
        shutil.copytree(db_dir, db_backup_dir + '/kinton')

    # Backup Abiquo Ontap Config
    if os.path.exists(abiquo_ontap_dir + '/tomcat/webapps/ROOT/WEB-INF/classes/config.xml'):
        os.makedirs(backup_dir +  '/ontap/config/')
    
    # Backup redis
    if os.path.exists(redis_db_file):
        os.makedirs(redis_backup_dir)
        shutil.copy(redis_db_file, redis_backup_dir)
    
    for i in range(1, 6):
        time.sleep(0.50)
        win.set(i)

    win.pop()
