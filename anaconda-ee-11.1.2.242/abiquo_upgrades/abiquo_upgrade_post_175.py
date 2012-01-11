import os
import iutil
import shutil
import logging
log = logging.getLogger("anaconda")

def abiquo_upgrade_post(anaconda):
    # write MOTD
    f = open(anaconda.rootPath + "/etc/motd", "w")

    f.write("""

                  Mb            
                  Mb            
                  Mb            H@
      ..J++...J,  Mb ..JJJ..    .,    .......    ..,      ...   ...+JJ.
    .dMY=!?7HNMP`.MNMB"??7TMm. .Mb  .JrC???7wo,  ,Hr      dM. .JM9=!?7WN,
   JHD`      ?#P .M#:      .HN..Hb .wZ!     .zw!`,Hr      dM`.d#!     ``Mr
   MN:        MP` MP`      `J#\.Hb ?O:       .rc ,Hr      dM`,HF        W#
   dMp       .HP` MN,      .dM`.Hb `OO.     .J?:`,Mb     .dM`.MN.      .Mt
    ?MNJ....gMMP .MMNa.....HB! .Hb  `zro...J?WN&. 7Mm....dM%` .WNa....+M=
      `7TYY"^ "^  "^ ?TYYY=`    7=   ` ????!``?TY   ?TYY"^`     .?TY9"=`
   
   

   Abiquo Release 1.7.5-GA

""")
    f.close()

    # apply the delta schema
    schema_path = anaconda.rootPath + "/usr/share/doc/abiquo-server/database/kinton-delta-1_7_0-to-1_7_5.sql"

    # Upgrade database if this is a server install
    if os.path.exists(schema_path):
        schema = open(schema_path)
        log.info("ABIQUO: Updating Abiquo 1.7.0 database...")
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
    backup_dir = anaconda.rootPath + '/opt/abiquo/backup/1.7.0'
    if os.path.exists('%s/fstab.anaconda' % backup_dir):
        shutil.copyfile("%s/fstab.anaconda" % backup_dir,
                '%s/etc/fstab' % anaconda.rootPath)

