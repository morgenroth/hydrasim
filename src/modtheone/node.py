'''
Created on 08.04.2010

@author: morgenro
'''

from modbasic import node

class TheOneNode(node.BasicNode):
    '''
    classdocs
    '''


    def __init__(self, name, address):
        '''
        Constructor
        '''
        node.BasicNode.__init__(self, name, address)
    
    def sendBundle(self, destination, size):
        self.ssh.execute("/bin/dd if=/dev/zero of=/tmp/testfile bs=1k count=" + (size / 1000))
        self.ssh.execute("/usr/bin/dtnsend " + destination + " /tmp/testfile")
