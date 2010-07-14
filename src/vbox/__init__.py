'''
Created on 29.03.2010

@author: morgenro
'''

import os
import re
from vbox.host import VirtualHost

def getHosts():
    hosts = []
    ret = os.popen("VBoxManage -q list vms")
    
    pattern = re.compile('"([\S\ ]+)"')
    
    for line in ret:
        try:
            m = pattern.match(line)
            hosts.append( VirtualHost( m.group(1) ) )
        except AttributeError:
            pass

    return hosts

