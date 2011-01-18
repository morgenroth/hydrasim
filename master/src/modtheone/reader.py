'''
Created on 15.03.2010

@author: morgenro
'''

import time
from utils import data

class ONELog(object):
    '''
    classdocs
    '''

    def __init__(self, file):
        self.file = file
        
    def getNodes(self):
        reader = ONEReader(self.file)
        self.nodes = {}
        
        while (reader.eof == False):
            evt = reader.next()
            
            if (evt.type == 'UP'):
                n1 = data.Node()
                n1.name = evt.node1
                n1.firstoccur = evt.time
                
                n2 = data.Node()
                n2.name = evt.node2
                n2.firstoccur = evt.time
                
                if (evt.node1 in self.nodes) == False:
                    self.nodes[evt.node1] = n1
                    
                if (evt.node2 in self.nodes) == False:
                    self.nodes[evt.node2] = n2
        
        return self.nodes.values()
    
    def getReader(self):
        return ONEReader(self.file)

class ONEEvent(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.time = 0.0
        self.type = 'UNKNOWN'
        self.node1 = None
        self.node2 = None
        self.size = 0

class ONEReader(object):
    '''
    classdocs
    '''

    def __init__(self, filename):
        '''
        Constructor
        '''
        self.eof = False
        self.file = open(filename, 'r')
        self.readline()
        
    def next(self):
        evt = ONEEvent()

        tmp = self.buffer.partition(':')
        evt.time = float(tmp[0])
        
        if (tmp[2].find('Connection UP') != -1):
            evt.type = 'UP'
            tmp = tmp[2].partition('Connection UP')
            tmp = tmp[2].partition('<->')
            evt.node1 = tmp[0].strip()
            evt.node2 = tmp[2].strip()
        
        if (tmp[2].find('Connection DOWN') != -1):
            evt.type = 'DOWN'
            tmp = tmp[2].partition('Connection DOWN')
            tmp = tmp[2].partition('<->')
            evt.node1 = tmp[0].strip()
            evt.node2 = tmp[2].strip()
            
        if (tmp[2].find('Message created') != -1):
            evt.type = 'MSG'
            tmp = tmp[2].partition('Message created')
            tmp = tmp[2].strip().split(' ')
            evt.node1 = tmp[0].strip()
            evt.node2 = tmp[1].strip()
            evt.size = tmp[3].strip()
        
        self.readline()
        return evt

    def readline(self):
        self.buffer = self.file.readline().strip('\n')
        
        if (self.buffer == ''):
            self.eof = True