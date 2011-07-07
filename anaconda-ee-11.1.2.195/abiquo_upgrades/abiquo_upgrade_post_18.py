import os
import iutil
import shutil
import logging
import ConfigParser

log = logging.getLogger("anaconda")

def abiquo_upgrade_post(anaconda):

    # apply the delta schema
    schema_path = anaconda.rootPath + "/usr/share/doc/abiquo-server/database/kinton-delta-1_7_6-to-1_8_0.sql"
    schema_path2 = anaconda.rootPath + "/usr/share/doc/abiquo-server/database/kinton-premium-delta-1.7.0-to-1.8.0.sql"

    # Upgrade database if this is a server install
    if os.path.exists(schema_path):
        schema = open(schema_path)
        log.info("ABIQUO: Updating Abiquo database (community delta)...")
        iutil.execWithRedirect("/sbin/ifconfig",
                                ['lo', 'up'],
                                stdout="/dev/tty5", stderr="/dev/tty5",
                                root=anaconda.rootPath)
        
        iutil.execWithRedirect("/etc/init.d/mysqld",
                                ['start'],
                                stdout="/mnt/sysimage/var/log/abiquo-postinst.log", stderr="//mnt/sysimage/var/log/abiquo-postinst.log",
                                root=anaconda.rootPath)

        iutil.execWithRedirect("/usr/bin/mysql",
                                ['kinton'],
                                stdin=schema,
                                stdout="/mnt/sysimage/var/log/abiquo-postinst.log", stderr="//mnt/sysimage/var/log/abiquo-postinst.log",
                                root=anaconda.rootPath)
        schema.close()
    
    if os.path.exists(schema_path2):
        schema = open(schema_path2)
        log.info("ABIQUO: Updating Abiquo database (premium delta)...")
        iutil.execWithRedirect("/sbin/ifconfig",
                                ['lo', 'up'],
                                stdout="/dev/tty5", stderr="/dev/tty5",
                                root=anaconda.rootPath)
        
        iutil.execWithRedirect("/etc/init.d/mysqld",
                                ['start'],
                                stdout="/mnt/sysimage/var/log/abiquo-postinst.log", stderr="//mnt/sysimage/var/log/abiquo-postinst.log",
                                root=anaconda.rootPath)

        iutil.execWithRedirect("/usr/bin/mysql",
                                ['kinton'],
                                stdin=schema,
                                stdout="/mnt/sysimage/var/log/abiquo-postinst.log", stderr="//mnt/sysimage/var/log/abiquo-postinst.log",
                                root=anaconda.rootPath)
        schema.close()

    # restore fstab
    backup_dir = anaconda.rootPath + '/opt/abiquo/backup/1.7.6'
    if os.path.exists('%s/fstab.anaconda' % backup_dir):
        shutil.copyfile("%s/fstab.anaconda" % backup_dir,
                '%s/etc/fstab' % anaconda.rootPath)


    # Add missing 1.8 properties
    sys_props = anaconda.rootPath + '/opt/abiquo/config/abiquo.properties'
    if os.path.exists(sys_props):
        log.info('ABIINSTALLENT: Updating system properties')
        try:
            config = ConfigParser.ConfigParser()
            config.optionxform = str
            config.read(sys_props)
            if config.has_section('remote-services'):
                    if not config.has_option('remote-services', 'abiquo.dvs.enabled'):
                            config.set('remote-services', 'abiquo.dvs.enabled', 'false')
                    if not config.has_option('remote-services', 'abiquo.dvs.vcenter.user'):
                            config.set('remote-services', 'abiquo.dvs.vcenter.user', 'changeme')
                    if not config.has_option('remote-services', 'abiquo.dvs.vcenter.password'):
                            config.set('remote-services', 'abiquo.dvs.vcenter.password', 'changeme')

            if config.has_section('server'):
                    if not config.has_option('server', 'abiquo.auth.module'):
                            config.set('server', 'abiquo.auth.module', 'abiquo')
                    if not config.has_option('server', 'abiquo.server.sessionTimeout'):
                            config.set('server', 'abiquo.server.sessionTimeout', '60')


            shutil.copyfile(sys_props, sys_props + '.before_18_update')
            ini_config = open(sys_props, 'w')
            config.write(ini_config)
        except Exception, e:
            log.error('ABIINSTALLENT: Exception writing new system properties %s' % e)
