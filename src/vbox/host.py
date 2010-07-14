'''
Created on 29.03.2010

@author: morgenro
'''

import os
import threading
import time

class VirtualHost(object):
    '''
    classdocs
    '''
    
    class RunMode:
        UNKNOWN = 0
        STOPPED = 1
        BOOTING = 2
        RUNNING = 3

    def __init__(self, name, headless = False, vrdp = False):
        '''
        Constructor
        '''
        self.master = None
        self.headless = headless
        self.vrdp = vrdp
        self.hasdisk = False
        self.name = name
        self.state = VirtualHost.RunMode.STOPPED
        
    def isRunning(self):
        return (self.state == VirtualHost.RunMode.RUNNING)
    
#    def getState(self):
#        ret = os.popen("VBoxManage -q showvminfo \"" + self.name + "\" --machinereadable")
#        
#        pattern = re.compile('^VMState="([\S\ ]+)"')
#        
#        for line in ret:
#            try:
#                m = pattern.match(line)
#                return m.group(1)
#            except AttributeError:
#                pass
#            
#        return "unknown"
    
    def start(self):
        if self.master == None:
            return
        
        if self.vrdp == True:
            self.master.execute("VBoxManage -q startvm " + self.name + " --type vrdp")
        elif self.headless == True:
            self.master.execute("VBoxManage -q startvm " + self.name + " --type headless")
        else:
            self.master.execute("VBoxManage -q startvm " + self.name)
        pass
    
    def stop(self):
        if self.master == None:
            return
        
        self.master.execute("VBoxManage -q controlvm " + self.name + " poweroff")
    
    def set(self, param, value):
        if self.master == None:
            return
        
        print("set vbox parameter " + param + " = " + value + " for node " + self.name)
        self.master.execute("VBoxManage -q modifyvm " + self.name + " --" + param + " " + value)
        pass
    
    def addHarddisk(self, image):
        if self.master == None:
            return
        
        # import the image to the vbox manager
        self.master.execute("VBoxManage -q openmedium disk " + image + " --type normal")
        
        # attach virtual disk to host
        if self.hasdisk == False:
            self.master.execute("VBoxManage -q storagectl " + self.name + " --name \"IDE-Controller\" --add ide")
            self.hasdisk = True

        self.master.execute("VBoxManage -q storageattach " + self.name + " --storagectl \"IDE-Controller\" --port 0 --device 0 --type hdd --medium " + image)
        self.image = image
        pass
    
    def removeHarddisk(self):
        if self.master == None:
            return
        
        if self.hasdisk == True:
            self.master.execute("VBoxManage -q storagectl " + self.name + " --name \"IDE-Controller\" --remove")
            
        self.master.execute("VBoxManage -q closemedium disk " + self.image)
        pass
        
    def remove(self):
        if self.master == None:
            return
        
        if self.hasdisk == True:
            self.master.execute("VBoxManage -q storagectl " + self.name + " --name \"IDE-Controller\" --remove")
            self.hasdisk = False
            
        self.master.execute("VBoxManage -q unregistervm " + self.name + " --delete")
        pass
    