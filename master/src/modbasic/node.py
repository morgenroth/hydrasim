'''
Created on 08.04.2010

@author: morgenro
'''

class BasicNode(object):
    '''
    classdocs
    '''

    def __init__(self, setup, name):
        '''
        Constructor
        '''
        self.name = name
        self.setup = setup
        self.cluster = setup.cc
        self.address = None
        self.x = None
        self.y = None
        self.z = None
        
    def setup(self):
        self.cluster.nodeSetup(self.name)
        
    def connectionUp(self, host):
        self.cluster.nodeConnectionUp(self.name, host)
        
    def connectionDown(self, host):
        self.cluster.nodeConnectionDown(self.name, host)
        
    def setPosition(self, x, y, z):
        if x != self.x or y != self.y or z != self.z: 
            self.x = x
            self.y = y
            self.z = z
            self.setup.nodePosition(self.name, self.x, self.y, self.z)
    