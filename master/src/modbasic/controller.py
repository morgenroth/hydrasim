'''
Created on 08.04.2010

@author: morgenro
'''
from mobility.mobilitymodel import MobilityModel

import sys
import time
from node import BasicNode
from vbox.host import VirtualHost

class BasicController(object):
    '''
    classdocs
    '''

    def __init__(self, setupdir, config):
        self.setupdir = setupdir
        self.config = config
        self.nodes = []
        self.mobility=None
        
        
        
        # get params for node generation
        numberOfNodes = int(config.get('modbasic', 'numberOfNodes'))
        currentAddress = config.get('domu', 'firstaddress')

        self.runtime  = 0
        if config.has_option('modbasic','minutes'):
            self.runtime=config.getint('modbasic','minutes')

        # create all nodes
        for nodeNumber in range(0,numberOfNodes):
            node = BasicNode(str(nodeNumber), currentAddress)
            currentAddress = self.increaseAddress(currentAddress)
            
            # set the basic options for each node
            self.readBaseOptions(config, node)

            # append the node to the node-list
            self.nodes.append(node)

            
    def readBaseOptions(self, config, node):
        options = [ "dns", "gateway", "netmask", "sshkey", "sshpubkey", "headless" ]
        for opt in options:
            exec("node." + opt + " = config.get('domu', opt)")
        
        # define the filename for the vdi image
        imagepath = config.get('domu', 'imagepath')
        node.image = str(node.name) + ".image"
        node.vdiimage = str(node.name) + ".vdi"
        
        # read virtualbox options
        node.vboxopts = {}
        node.vboxopts["vrdp"] = "off"
        
        for opt in config.options('vbox'):
            node.vboxopts[opt] = config.get('vbox', opt)
            
        # create a vhost object
        node.vhost = VirtualHost(node.name, (node.headless == "1"), (node.vboxopts["vrdp"] == "on"))
            
    def getNodes(self):
        return self.nodes
    
    def getNode(self, name):
        for n in self.nodes:
            if n.name == name:
                return n
        return None
    
    def run(self):
        if self.config.has_section('mobility'):
            self.mobility = MobilityModel(self.config, self.nodes)
            self.mobility.start()

        self.waitForSimulationEnd()

    def waitForSimulationEnd(self):
        if self.runtime == 0 or self.runtime == -1:
            print("No timeout. Run until user aborts")
            print ("- run simulation -")
            raw_input(u'Press key to abort.')
        else:
            print("Running for "+str(self.runtime)+" minutes")
            time.sleep(self.runtime*60)



    def shutdown(self):
        print("Shutting down")
        if self.mobility != None:
            print("Shutdown mobility model")
            self.mobility.stop()

    def increaseAddress(self, ip):
        #print("IP "+str(ip))
        octets=ip.split('.')
        octets[3]=int(octets[3])+1
        if octets[3] > 253:
           octets[3]=1
           octets[2]=int(octets[2])+1
           if octets[2] > 253:
               print("Out of IPs!")
               sys.exit(-100)
        return str(octets[0])+"."+str(octets[1])+"."+str(octets[2])+"."+str(octets[3])