import os
import iutil

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
   
   

   Abiquo Release 1.7.0

""")
    f.close()

    # Migrate redis db to 1.7
    if os.path.exists(anaconda.rootPath + '/opt/abiquo/tomcat/webapps/vsm') and \
            os.path.exists(anaconda.rootPath + '/etc/init.d/redis'):
                log.info("Migrating Abiquo 1.6.8 redis database...")
                # loopback up
                iutil.execWithRedirect("/sbin/ifconfig",
                                        ['lo', 'up'],
                                        stdout="/dev/tty5", stderr="/dev/tty5",
                                        root=anaconda.rootPath)
                # redis up
                iutil.execWithRedirect("/usr/sbin/redis-server",
                                        ['/etc/redis.conf'],
                                        stdout="/dev/tty5", stderr="/dev/tty5",
                                        root=anaconda.rootPath)
                # apply update
                iutil.execWithRedirect("/bin/bash",
                                        ['/opt/abiquo/tools/migrate-abiquo-16-redis/migrate.sh'],
                                        stdout="/mnt/sysimage/var/log/migrate-redis-16", stderr="/mnt/sysimage/var/log/migrate-redis-16",
                                        root=anaconda.rootPath)


    #
    # Disable abiquo-tomcat service so we can run upgrade scripts safely
    # the first time the system starts after the upgrade
    #
    #if os.path.exists(anaconda.rootPath + '/etc/init.d/abiquo-tomcat'):
    #    iutil.execWithRedirect("/sbin/chkconfig",
    #                            ['abiquo-tomcat', "off"],
    #                            stdout="/dev/tty5", stderr="/dev/tty5",
    #                            root=anaconda.rootPath)
    #
    # make sure rabbitmq-server is started in the Abiquo Server box
    #
    if os.path.exists(anaconda.rootPath + '/etc/init.d/rabbitmq-server'):
        iutil.execWithRedirect("/sbin/chkconfig",
                                ['rabbitmq-server', "on"],
                                stdout="/dev/tty5", stderr="/dev/tty5",
                                root=anaconda.rootPath)

    #
    # Write the new (1.7) properties file in the RS and Server box
    # 
    if os.path.exists(anaconda.rootPath + '/opt/abiquo/backup/1.6.8/configs/virtualfactory.xml') or \
            os.path.exists(anaconda.rootPath + '/opt/abiquo/backup/1.6.8/configs/server.xml'):
        os.putenv('ABIQUO_CONFIG_HOME', '/opt/abiquo/backup/1.6.8/configs/')
        os.putenv('ABIQUO_PROPERTIES', '/opt/abiquo/config/abiquo.properties')
        iutil.execWithRedirect("/opt/abiquo/tools/migrate-abiquo-16-xml-configs", [''],
                                stdout="/dev/tty5", stderr="/dev/tty5",
                                root=anaconda.rootPath)
        f = open(anaconda.rootPath + "/opt/abiquo/config/.needsupgrade", "w")
        f.write("17-nuclear-launch\n")
        f.close()
