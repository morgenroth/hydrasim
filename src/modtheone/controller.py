'''
Created on 08.04.2010

@author: morgenro
'''

import sys

from vbox.host import VirtualHost
from modtheone import reader
from modtheone.node import TheOneNode
from modbasic import controller
import time

class TheOneController(controller.BasicController):
    '''
    classdocs
    '''

    def __init__(self, setupdir, config):
        self.setupdir = setupdir
        self.config = config
        self.nodes = []
        
        self.onelog = reader.ONELog(setupdir + "/" + config.get('modtheone', 'logfile'))
        
        # get params for node generation
        currentAddress = config.get('domu', 'firstaddress')
        
        # create all nodes
        for n in self.onelog.getNodes():
            node = TheOneNode(n.name, currentAddress)
            currentAddress = self.increaseAddress(currentAddress)
            
            # set the basic options for each node
            self.readBaseOptions(config, node)

            # append the node to the node-list
            self.nodes.append(node)
    
    def run(self):
        print ("- run simulation -")
        # get a reader for the logfile of TheONE
        logreader = self.onelog.getReader()
        current_time = 0.0

        while (logreader.eof == False):
            evt = logreader.next()
            if (evt.type == 'UNKNOWN'):
                continue
            
            if (evt.time != current_time):
                #if max_time < evt.time:
                #    break
                
                print 'Wait', (evt.time - current_time), 'seconds'
                time.sleep(evt.time - current_time)
                current_time = evt.time
            
            host1 = self.getNode(evt.node1)
            if (host1 != None):
                host2 = self.getNode(evt.node2)
                if (host2 != None):
                    if evt.type == "UP":
                        #iptables.connectionUp(host1, host2)
                        host1.connectionUp(host2)
                        host2.connectionUp(host1)
                        print "connection up between", host1.name, "and", host2.name
                    if evt.type == "DOWN":
                        host1.connectionDown(host2)
                        host2.connectionDown(host1)
                        #iptables.connectionDown(host1, host2)
                        print "connection down between", host1.name, "and", host2.name
                    if evt.type == "MSG":
                        host1.sendBundle("dtn://" + host2.name + "/test", evt.size)
                        print "bundle created, src: " + host1.name + ", dst: " + host2.name + ", size: " + evt.size
        pass
    