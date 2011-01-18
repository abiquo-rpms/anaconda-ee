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

class Abiquo:

    def writeKS(self, f):
	f.write("abiquo-server --ip=%s --dbhost=%s --dbpassword=%s --dbuser=%s\n" % \
                (self.abiquo_server_ip,
                 self.abiquo_db_host,
                 self.abiquo_db_password,
                 self.abiquo_db_user
                 )
                )

    def write(self, instPath):
        # dont do this in test mode!
        if flags.test:
            return
        
        f = open(instPath + "/etc/motd", "w")

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

        f = open(instPath + "/opt/abiquo/config/abiquo.properties", 'a')
        f.write("[server]\n")
        f.write("abiquo.server.sessionTimeout = %s\n" %
                self.abiquo_server_sessionTimeout)
        f.write("abiquo.server.mail.server = %s\n" % self.abiquo_server_mail_server)
        f.write("abiquo.server.mail.user = %s\n" % self.abiquo_server_mail_user )
        f.write("abiquo.server.mail.password = %s\n" %
                self.abiquo_server_mail_password )
        f.write("abiquo.server.api.location = %s\n" %
                self.abiquo_server_api_location)
        f.write("abiquo.rabbitmq.username = %s\n" %
                self.abiquo_rabbitmq_username)
        f.write("abiquo.rabbitmq.password = %s\n" %
                self.abiquo_rabbitmq_password)
        f.write("abiquo.rabbitmq.host = %s\n" %
                self.abiquo_rabbitmq_host)
        f.write("abiquo.rabbitmq.port = %s\n" %
                self.abiquo_rabbitmq_port)
        f.write("abiquo.database.user = %s\n" %
                self.abiquo_database_user)
        f.write("abiquo.database.password = %s\n" %
                self.abiquo_database_password )
        f.write("abiquo.database.host = %s\n" %
                self.abiquo_database_host )
        f.close()


    def __init__(self):
        self.logo = 'abiquo'
        self.abiquo_server_ip = '127.0.0.1'
        self.abiquo_db_user = 'root'
        self.abiquo_db_password = ''
        self.abiquo_db_host = 'localhost'
        self.abiquo_rs_ip = '127.0.0.1'
        self.selectedGroups = []
        self.abiquo_server_sessionTimeout = '60'
        self.abiquo_server_mail_server= '127.0.0.1'
        self.abiquo_server_mail_user= 'none@none.es'
        self.abiquo_server_mail_password = 'none'
        self.abiquo_server_api_location = 'http://localhost/api/'
        self.abiquo_rabbitmq_username = 'guest'
        self.abiquo_rabbitmq_password = 'guest'
        self.abiquo_rabbitmq_host = '127.0.0.1'
        self.abiquo_rabbitmq_port = '5672'
        self.abiquo_database_host = '127.0.0.1'
        self.abiquo_database_user = 'root'
        self.abiquo_database_password = ''



