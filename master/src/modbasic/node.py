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
        self.cluster = setup.cc
        self.address = None
        
    def setup(self):
        self.cluster.nodeSetup(self.name)
        
    def connectionUp(self, host):
        self.cluster.nodeConnectionUp(self.name, host)
        
    def connectionDown(self, host):
        self.cluster.nodeConnectionDown(self.name, host)
        