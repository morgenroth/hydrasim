'''
Created on 08.04.2010

@author: morgenro
'''
from mobility.mobilitymodel import MobilityModel

import sys
import time
from node import BasicNode

class BasicController(object):
    '''
    classdocs
    '''

    def __init__(self, setup):
        self.setup = setup
        self.nodes = []
        self.mobility=None

        # get params for node generation
        numberOfNodes = int(setup.config.get('modbasic', 'max_nodes'))

        self.runtime  = 0
        if setup.config.has_option('modbasic','minutes'):
            self.runtime = setup.config.getint('modbasic','minutes')

        # create all nodes
        for nodeNumber in range(0,numberOfNodes):
            node = BasicNode(setup, "node" + str(nodeNumber))
            
            # append the node to the node-list
            self.nodes.append(node)
            
    def getNodes(self):
        return self.nodes
    
    def getNode(self, name):
        for n in self.nodes:
            if n.name == name:
                return n
        return None
    
    def run(self):
        if self.setup.config.has_section('mobility'):
            self.mobility = MobilityModel(self.setup)
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
