'''
Created on 08.04.2010

@author: morgenro
'''
import time
import sys
import os

import socket
import select
import struct

import libvirt
from xml.dom import minidom
import shutil

import ConfigParser
import threading
import visualization

class Slave:
    '''
    classdocs
    '''
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ready = True
        self.readbuf = ""
        self.nodes = []
        
    def connect(self, port):
        try:
            self.sock.connect((self.address[0], port))
        except socket.error:
            print("failed to connect to " + self.name)
        
    def hasNode(self, name):
        for n in self.nodes:
            if n.name == name:
                return True
        return False
    
    """ get all real address of the nodes """
    def fetchAddressList(self):
        """
        answer is a list of nodes with the corresponding address terminated by an "EOL"
        node01 10.0.0.1
        node02 10.0.0.2
        node03 10.1.0.1
        ...
        EOL
        """
        try:
            self.sock.send("ACTION\nLIST\n")
            
            """ set ready state to false """
            self.ready = False
            
            while not self.ready:
                msg = self.readMessage()
                if msg == "EOL":
                    self.ready = True
                else:
                    (name, address) = msg.split(" ", 1)
                    self.setNodeAddress(name, address)
        except socket.error:
            print("failed to fetch LIST from " + self.name)
    
    def setNodeAddress(self, name, address):
        for n in self.nodes:
            if n.name == name:
                n.address = address
                
    def getNodeAddress(self, name):
        for n in self.nodes:
            if n.name == name:
                return n.address
        return None
    
    def nodeSetup(self, name):
        try:
            self.sock.send("ACTION\nSETUP " + name + "\n")
        except:
            pass
        
    def nodeScript(self, name, script):
        try:
            self.sock.send("ACTION\nSCRIPT " + name + " " + script + "\n")
        except:
            pass
        
    def nodeConnectionUp(self, name, address):
        try:
            self.sock.send("ACTION\nUP " + name + " " + address + "\n")
        except:
            pass
        
    def nodeConnectionDown(self, name, address):
        try:
            self.sock.send("ACTION\nDOWN " + name + " " + address + "\n")
        except:
            pass
    
    def prepare(self, url):
        """ set ready state to false """
        self.ready = False
        
        try:
            self.sock.send("PREPARE\n" + url + "\n")
        except socket.error:
            self.ready = True
            print("failed to send PREPARE to " + self.name)
    
    def run(self):
        """ set ready state to false """
        self.ready = False
        
        try:
            self.sock.send("RUN\n")
        except socket.error:
            self.ready = True
            print("failed to send RUN to " + self.name)
    
    def stop(self):
        """ set ready state to false """
        self.ready = False
        
        try:
            self.sock.send("STOP\n")
        except socket.error:
            self.ready = True
            print("failed to send STOP to " + self.name)
    
    def cleanup(self):
        """ set ready state to false """
        self.ready = False
        
        try:
            self.sock.send("CLEANUP\n")
        except socket.error:
            self.ready = True
            print("failed to send CLEANUP to " + self.name)
        
    def readMessage(self):
        try:
            while not "\n" in self.readbuf:
                self.readbuf = self.readbuf + self.sock.recv(1500)
                
            (line, self.readbuf) = self.readbuf.split("\n", 1)
            return line.strip()
        except socket.error:
            return None
    
    def quit(self):
        try:
            self.sock.send("QUIT\n")
        except socket.error:
            print("failed to send QUIT to " + self.name)

class ClusterControl:
    '''
    classdocs
    '''
    def __init__(self, mcast_interface = ""):
        '''
        Constructor
        '''
        self.slaves = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        
        ''' Make the socket multicast-aware, and set TTL. '''
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 20) # Change TTL (=20) to suit
        self.sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)
        self.sock.bind((mcast_interface, 0))
        
    def scan(self, addr, timeout = 5):
        ''' create an empty list '''
        list = []
        self.slaves = []
        
        ''' send out a discovery request '''
        self.sock.sendto('\x00' + "HELLO", addr)
        
        read_list = []
        write_list = []
        exc_list = []
        
        read_list.append(self.sock)
        
        retry = True
        
        while retry:
            (in_, out_, exc_) = select.select(read_list, write_list, exc_list, timeout)
            retry = False
        
            for fd in in_:
                retry = True
                (data, address) = fd.recvfrom(1024)
                values = struct.unpack_from("!BI", data)
                if values[0] == 1:
                    itm = (data[5:(values[1]+5)], address)
                    list.append(itm)
                    self.slaves.append( Slave(itm[0], address) )
                
            for fd in out_:
                pass

            for fd in exc_:
                pass
            
        return list
    
    def connect(self, port):
        """ connect to all slaves """
        for s in self.slaves:
            s.connect(port)
        
    def prepare(self, url):
        """ send out a prepare message to all cluster nodes """
        for s in self.slaves:
            s.prepare(url)
        
        """ wait until all cluster nodes are ready """
        self.wait_ready()
    
    def run(self):
        """ send out a run message to all cluster nodes """
        for s in self.slaves:
            s.run()
        
        """ wait until all cluster nodes are ready """
        self.wait_ready()
        
        """ fetch all node lists of each slave """
        for s in self.slaves:
            s.fetchAddressList()
            
    def script(self, script):
        """ run custom setup script on each node """
        for s in self.slaves:
            for n in s.nodes:
                s.nodeScript(n.name, script)
        
    def stop(self):
        """ send out a stop message to all cluster nodes """
        for s in self.slaves:
            s.stop()
        
        """ wait until all cluster nodes are ready """
        self.wait_ready()
        
        """ quit the connection """
        for s in self.slaves:
            s.quit()
        
    def cleanup(self):
        """ send out a cleanup message to all cluster nodes """
        for s in self.slaves:
            s.cleanup()
        
        """ wait until all cluster nodes are ready """
        self.wait_ready()
    
    def wait_ready(self, timeout = 3600):
        read_list = []
        write_list = []
        exc_list = []
        
        """ fill the read list """
        for s in self.slaves:
            read_list.append(s.sock)
        
        while not self.isReady():
            (in_, out_, exc_) = select.select(read_list, write_list, exc_list, timeout)
            
            for fd in in_:
                s = self.getSlave(fd)
                msg = s.readMessage()
                if msg == "READY":
                    s.ready = True
                
            for fd in out_:
                pass

            for fd in exc_:
                s = self.getSlave(fd)
                print "slave went down (" + s.name + ")"
        
    def isReady(self):
        for s in self.slaves:
            if not s.ready:
                return False
            
        return True
            
    def getSlave(self, sockid):
        for s in self.slaves:
            if s.sock == sockid:
                return s
        return None
    
    def getSlaveOf(self, node):
        for s in self.slaves:
            if s.hasNode(node):
                return s
        return None
    
    def nodeScript(self, name, script):
        s = self.getSlaveOf(name)
        if s != None:
            print("call script on " + name)
            print(script)
            s.nodeScript(name, script)
    
    def nodeSetup(self, name):
        s = self.getSlaveOf(name)
        if s != None:
            print("call node setup for " + name)
            s.nodeSetup(name)
            
    def nodeGetAddress(self, name):
        for s in self.slaves:
            addr = s.getNodeAddress(name)
            if addr != None:
                return addr
        return None
    
    def nodeConnectionUp(self, name, host):
        print("connection up " + name + " -> " + host.name)
        s = self.getSlaveOf(name)
        if s != None:
            addr = self.nodeGetAddress(host.name)
            if addr != None:
                s.nodeConnectionUp(name, addr)
    
    def nodeConnectionDown(self, name, host):
        print("connection down " + name + " -> " + host.name)
        s = self.getSlaveOf(name)
        if s != None:
            addr = self.nodeGetAddress(host.name)
            if addr != None:
                s.nodeConnectionDown(name, addr)

class Setup(object):
    '''
    classdocs
    '''
    
    def __init__(self, config, setupname, datadir):
        self.config = config
        self.name = setupname
        self.datadir = datadir
        self.basedir = self.datadir + "/base"
        self.servdir = self.datadir + "/serv/" + self.name
        self.setupdir = self.datadir + "/setups/" + self.name
        self.template_base_file = self.setupdir + "/" + self.config.get("template", "image")
        
        ''' use the template image in the base directory if the specific not exists '''
        if not os.path.isfile(self.template_base_file):
            self.template_base_file = self.basedir + "/" + self.config.get("template", "image")
            
        self.cc = None
        self.vizapi = visualization.VizServer((self.config.get("general", "mcast_interface"), 5000))
        
    def loadController(self):
        """ import the module """
        modulename = self.config.get('general','module')
        ctrl = None
        exec("import " + modulename)
        exec("ctrl = " + modulename + ".getController(self)")
        return ctrl
        
    def exit(self):
        self.cc.stop()
        
    def nodePosition(self, name, x, y, z):
        self.vizapi.nodePosition(name, x, y, z)

    def sudo(self, command):
        print "superuser execution:"
        print command
        
        if self.config.get('general', 'sudomode') == "plain":
            os.system("sudo " + str(command))
        elif self.config.get('general', 'sudomode') == "gksu":
            os.system("gksu '" + str(command) + "'")
    
    def __init_cluster(self):
        if self.cc != None:
            return
        
        """ discover the slaves """
        try:
            self.cc = ClusterControl(self.config.get("general", "mcast_interface"))
        except ConfigParser.NoOptionError:
            self.cc = ClusterControl()
        
        answer = None
        while answer != "yes":
            """ scan for slaves """
            nodes = self.cc.scan( ("225.16.16.1", 3234), 1 )
            
            nodelist_txt = ""
            for n in nodes:
                nodelist_txt = nodelist_txt + n[0] + " (" + n[1][0] + "), "
                
            print "Available nodes: " + nodelist_txt.strip().rstrip(",")
            
            try:
                answer = raw_input('Are all slaves discovered? (yes/no/abort): ')
                if answer == "abort":
                    sys.exit(-1)
            except KeyboardInterrupt:
                sys.exit(-1)
        
        """ load the controller """
        self.ctrl = self.loadController()
        
        """ create configuration per slave """
        self.prepareSlaveConfiguration()
        
        """ connect to all slaves """
        self.cc.connect(4242)
        
    def prepare(self):
        """ initialize the cluster """
        self.__init_cluster()
        
        """ create serv folder """
        try:
            os.makedirs(self.servdir)
        except OSError:
            pass
        
        """ prepare the image template """
        self.prepareTemplateImage()
        
        """ copy the list of monitor nodes """
        shutil.copy(os.path.join(self.setupdir, "monitor-nodes.txt"), os.path.join(self.servdir, "monitor-nodes.txt"))
        
        """ copy node specific scripts """
        shutil.copy(os.path.join(self.basedir, "prepare_image_node.sh"), os.path.join(self.servdir, "prepare_image_node.sh"))
        shutil.copy(os.path.join(self.setupdir, "modify_image_node.sh"), os.path.join(self.servdir, "modify_image_node.sh"))
        
        """ copy libvirt templates """
        for f in os.listdir(self.basedir):
            if f.startswith("node-template.") and f.endswith(".xml"):
                shutil.copy(os.path.join(self.basedir, f), os.path.join(self.servdir, f))
                
        for f in os.listdir(self.setupdir):
            if f.startswith("node-template.") and f.endswith(".xml"):
                shutil.copy(os.path.join(self.setupdir, f), os.path.join(self.servdir, f))
        
        """ copy magicmount script """
        shutil.copy(self.basedir + "/magicmount.sh", self.servdir + "/magicmount.sh")
        
        """ send out prepare command """
        url = self.config.get("general", "url")
        self.cc.prepare(url + "/" + self.name)
    
    def prepareSlaveConfiguration(self):
        nodes = self.ctrl.getNodes()
        max_nodes = int(self.config.get("general", "max_slave_nodes"))
        offset = 0
        
        for slave in self.cc.slaves:
            i = 0
            
            """ create private folder for the slave """
            try:
                os.makedirs(self.servdir + "/" + slave.name)
            except OSError:
                pass
        
            """ generate a node list """
            fd = open(self.servdir + "/" + slave.name + "/nodes.txt", "w")
            slave.nodes = []
            
            try:
                while i < max_nodes:
                    fd.write(nodes[offset + i].name + "\n")
                    slave.nodes.append( nodes[offset + i] )
                    i = i + 1
            except IndexError:
                pass
            
            offset = offset + i
            fd.close()
    
    def prepareTemplateImage(self):
        print("Copying base image....")
        template_image = self.servdir + "/template.image"
        shutil.copy(self.template_base_file, template_image)
        
        print("Basic image preparation")
        self.sudo("/bin/bash " + self.basedir + "/prepare_image_base.sh " + template_image + " " + self.basedir + " " + self.setupdir)
    
    def storeVirtTemplate(self, filename):
        ''' open a local virtual box session '''
        conn = libvirt.open(self.config.get("template", "virturl"))
        if conn == None:
            print 'Failed to open connection to the hypervisor'
            sys.exit(1)
        
        ''' get xml for the template host '''
        tpl_host = conn.lookupByName(self.config.get("template", "virtname"))
        
        xml = tpl_host.XMLDesc(0)
        doc = minidom.parseString(xml)
        
        ''' remove all unique elements: UUID, MAC, dist source file '''
        for id in doc.getElementsByTagName("uuid"):
            id.parentNode.removeChild(id)
            
        for mac in doc.getElementsByTagName("mac"):
            if mac.hasAttribute("address"):
                mac.removeAttribute("address")
        
        for disk in doc.getElementsByTagName("disk"):
            source = disk.getElementsByTagName("source")[0]
            if source.hasAttribute("file"):
                source.setAttribute("file", "not-set")
        
        fd = open(filename, "w")
        fd.write(doc.toxml())
        fd.close()
        
    def run(self):
        """ initialize the visualization api """
        self.vizapi.startup()
        
        """ initialize the cluster """
        self.__init_cluster()
        self.cc.run()
        
        """ call custom setup script on each node in the cluster """
        try:
            fd = open(os.path.join(self.setupdir, "setup.txt"), "r")
            for line in fd.readlines():
                if len(line) > 0:
                    self.cc.script(line)
        except IOError:
            ''' no custom setup script exists '''
            pass
        
        """ run custom simulation """
        self.ctrl.run()
        self.ctrl.shutdown()
        
        """ shutdown viz api """
        self.vizapi.shutdown()
    
    """ cleanup the setup """
    def cleanup(self):
        """ initialize the cluster """
        self.__init_cluster()
        self.cc.cleanup()
        
