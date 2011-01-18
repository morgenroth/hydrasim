'''
Created on 27.04.2010

@author: morgenro
'''

import threading

import os
from vbox import host
from utils import ssh
import Queue

import ConfigParser
import shutil

def getVBoxMasters(config, datadir, setupdir, tmpdir):
    ret = []
    try:
        for name in config.get("cluster", "names").split(" "):
            type = config.get(name, "type")
            
            if type == "ssh":
                ret.append(VBoxBufferedMasterSSH(config, name, datadir, setupdir, tmpdir))
            else:
                ret.append(VBoxMasterLocal(config, name, datadir, setupdir, tmpdir))
    except ConfigParser.NoSectionError:
        ret = [ VBoxMasterLocal(config, "localhost", datadir, setupdir, tmpdir) ]
    
    return ret

class VBoxMaster(object):
    '''
    classdocs
    '''

    def __init__(self, config, name, datadir, setupdir, tmpdir):
        '''
        Constructor
        '''
        self.name = name
        self.datadir = datadir
        self.setupdir = setupdir
        self.tmpdir = tmpdir
        
        # read configuration parameter
        self.options = {}
        for opt in config.options(name):
            self.options[opt] = config.get(name, opt)
            
        self.lastvrdp = int(self.options["vrdpport"])

    def commit(self):
        pass
            
    def close(self):
        pass
        
    def upload(self, file):
        pass
    
    def execute(self, cmd):
        pass
    
    def copy(self, source, destination):
        pass
    
    def getVrdpPort(self):
        self.lastvrdp = self.lastvrdp + 1
        return self.lastvrdp
    
    def newNode(self, hostname, tmpdir):
        print u"-> creating vbox-host", hostname
        
        # delete old image and host
        self.deleteHost(hostname)
        
        self.deleteImage(tmpdir + "/pyemulation-" + hostname + ".vdi")
        self.execute("rm " + tmpdir + "/pyemulation-" + hostname + ".vdi")
        
        # create a new virtual host
        vhost = self.createHost(hostname)
        
        # setup network for host
        self.setupNetwork(vhost)
        
        # set all parameters for this host
        self.setParameter(vhost)
        
        return vhost
    
    def getHost(self, hostname):
        return host.VirtualHost("pyemulation-" + hostname)
    
    def createHost(self, hostname):
        # create a new vbox host
        self.execute("VBoxManage createvm --name pyemulation-" + hostname + " --register")
        return host.VirtualHost("pyemulation-" + hostname)
    
    def deleteHost(self, name):
        self.execute("VBoxManage storagectl pyemulation-" + name + " --name \"IDE-Controller\" --remove")
        self.execute("VBoxManage unregistervm pyemulation-" + name + " --delete")
        pass
    
    def deleteImage(self, image):
        self.execute("VBoxManage closemedium disk " + image)
        pass
    
    def setupNetwork(self, vhost):
        pass
    
    def setParameter(self, vhost):
        params = {'memory': '64', 'uart1': '0x3F8 4', 'nic1': 'hostonly', 'hostonlyadapter1': 'vboxnet0'}
        
        for param, value in params.iteritems():
            vhost.set(param, value)
        pass
    
    def convertImage(self, src, dst):
        # delete old image
        self.execute("rm " + dst)
        
        # create the new image
        self.execute("VBoxManage convertfromraw " + src + " " + dst + " --format VDI --variant Standard")
        pass
    
    def cloneImage(self, src, dst):
        # delete old image
        self.execute("rm " + dst)
        self.execute("VBoxManage clonehd " + src + " " + dst)
    
    def disableDHCPServer(self, staticip):
        self.execute("VBoxManage dhcpserver remove --ifname vboxnet0")
        self.execute("VBoxManage hostonlyif ipconfig vboxnet0 --ip " + staticip)
        pass
    
    def enableDHCPServer(self, ip):
        self.execute("VBoxManage hostonlyif ipconfig vboxnet0 --ip "+str(ip))
        self.execute("VBoxManage dhcpserver add --ifname vboxnet0 --ip 192.168.56.254 --netmask 255.255.255.0 --lowerip 192.168.56.100 --upperip 192.168.56.200 --enable")
        pass
    
    def createVM(self, name):
        self.execute("VBoxManage -q createvm --name "+name+" --register")
    
    
    def setParam(self, machine, param, value):
        print("set vbox parameter " + param + " = " + str(value) + " for node " + machine)
        self.execute("VBoxManage -q modifyvm " + machine + " --" + param + " " + str(value))
    
    
    def configWith(self, machine, params):
        for param, value in params.iteritems():
            self.setParam(machine, param, value)
            if (param == "vrdp") and (value == "on"):
                self.setParam(machine, "vrdpport", str(self.getVrdpPort()))
    
    def createHD(self, image, dest):
         self.execute("VBoxManage -q convertfromraw " + image + " " + dest + " --format VDI --variant Standard")
    
    
    def connectHd(self, machine, disk):
        self.execute("VBoxManage -q openmedium disk " + disk + " --type normal")
    
        # attach virtual disk to host
        self.execute("VBoxManage -q storagectl " + machine + " --name \"IDE-Controller\" --add ide")
        self.execute("VBoxManage -q storageattach " + machine + " --storagectl \"IDE-Controller\" --port 0 --device 0 --type hdd --medium " + disk)
    
       
    
    def createAndConnectHd(self, machine, image, dest):
        self.execute("VBoxManage -q convertfromraw " + image + " " + dest + " --format VDI --variant Standard")
        self.execute("VBoxManage -q openmedium disk " + dest + " --type normal")
    
        # attach virtual disk to host
        self.execute("VBoxManage -q storagectl " + machine + " --name \"IDE-Controller\" --add ide")
        self.execute("VBoxManage -q storageattach " + machine + " --storagectl \"IDE-Controller\" --port 0 --device 0 --type hdd --medium " + dest)
    
    
    def setVBox0IP(self, staticip):
        self.execute("VBoxManage -q dhcpserver remove --ifname vboxnet0")
        self.execute("VBoxManage -q hostonlyif ipconfig vboxnet0 --ip " + staticip)
    
    def startVM(self, machine, headless = False):
        if headless == True:
            self.execute("VBoxHeadless -s " + machine)
        else:
            self.execute("VBoxManage -q startvm " + machine)
    
    
    def unregisterVM(self, machine):
        self.execute("VBoxManage -q storagectl "+machine+" --name \"IDE-Controller\" --remove")
        self.execute("VBoxManage -q unregistervm " + machine + " --delete")
    
    
    def removeImage(self, image):
        self.execute("VBoxManage -q closemedium disk " + image)
        pass
    

class VBoxMasterLocal(VBoxMaster):
    
    def __init__(self, config, name, datadir, setupdir, tmpdir):
        try:
            VBoxMaster.__init__(self, config, name, datadir, setupdir, tmpdir)
        except ConfigParser.NoSectionError:
            self.options["type"] = "local"
            self.options["maxnodes"] = None
            self.options["tmpdir"] = "/tmp"
    
    def execute(self, cmd):
        os.system(cmd)
        
    def copy(self, source, target):
        shutil.copy(source, target)
        
    def upload(self, file):
        self.copy(file, self.options["tmpdir"] + "/")
        pass

    def remove(self, file):
        os.remove(file)
        pass
        
    def sudo(self, cmd):
        self.execute("sudo " + cmd)
        pass
    
class VBoxMasterSSH(VBoxMaster):
    
    def __init__(self, config, name, datadir, setupdir, tmpdir):
        VBoxMaster.__init__(self, config, name, datadir, setupdir, tmpdir)
        
        try:
            self.ssh = ssh.RemoteHost(self.options["host"], self.options["user"], None, datadir + "/" + self.options["sshkey"])
            self.ssh.connect()
        except:
            # connection failed or refused
            self.ssh = None
    
    def copy(self, source, target):
        self.execute("cp -vf " + source + " " + target)

    def execute(self, cmd):
        if self.ssh != None:
            self.ssh.execute(cmd)
        pass
    
    def upload(self, file):
        if self.ssh != None:
            self.ssh.put(file, self.options["tmpdir"] + "/")
        pass
    
    def remove(self, file):
        self.execute("rm -vrf " + file)
        pass
        
    def sudo(self, cmd):
        self.execute(cmd)
        pass
    
    def close(self):
        if self.ssh != None:
            self.ssh.close() 
        pass
    
class VBoxBufferedMasterSSH(VBoxMasterSSH):
    
    class DelayedExecutionAgent(threading.Thread):
        def __init__(self, master):
            threading.Thread.__init__(self)
            self.master = master
            self.queue = Queue.Queue()
            self.running = True
            
        def run(self):
            while self.running:
                try:
                    buffer = self.queue.get(True, 1)
                    
                    # create a batch file
                    filename_local = self.master.tmpdir + "/" + self.master.name + "-batch.run"
                    filename_remote = self.master.options["tmpdir"] + "/" + self.master.name + "-batch.run"
                    file = open(filename_local, "w")
                    file.write("#!/bin/bash\n#\n")
                    
                    for cmd in buffer:
                        print(self.master.name + ":# " + cmd)
                        file.write(cmd + "\n")
                    
                    file.close()
                    VBoxMasterSSH.upload(self.master, filename_local)
                    VBoxMasterSSH.execute(self.master, "/bin/bash " + filename_remote)
                    
                    self.queue.task_done()
                except:
                    pass
        
        def add(self, job):
            self.queue.put(job)
        
        def wait(self):
            self.queue.join()
            
        def stop(self):
            self.wait()
            self.running = False
            self.join()
    
    def __init__(self, config, name, datadir, setupdir, tmpdir):
        VBoxMasterSSH.__init__(self, config, name, datadir, setupdir, tmpdir)
        self.agent = VBoxBufferedMasterSSH.DelayedExecutionAgent(self)
        self.agent.start()
        self.buffer = []
        self.upbuffer = []
    
    def execute(self, cmd):
        self.buffer.append(cmd)
        
    def upload(self, file):
        self.upbuffer.append(file)

    def close(self):
        self.commit()
        self.agent.stop()
        VBoxMasterSSH.close(self)

    def commit(self):
        for file in self.upbuffer:
            print("uploading " + file + " to " + self.name)
            VBoxMasterSSH.upload(self, file)
        
        self.agent.add(self.buffer)
        
        self.buffer = []
        self.upbuffer = []
