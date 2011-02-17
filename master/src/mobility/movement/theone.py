'''
Created on 17.02.2011

@author: morgenro
'''

import threading
import os
import time
import math

class Movement(object):
    
    def __init__(self, nodes, setupdir, config):
        self.filename = os.path.join(setupdir, config.get("movement", "file"))
        self.reader = None
        self.nodes = nodes

        # by default all nodes are disabled
        for n in self.nodes:
            n.disabled = True
            n.range = float(config.get("movement", "range"))
    
    def start(self):
        self.reader = MovementReader(self.filename, self.nodes)
        self.reader.start()

    def stop(self):
        self.reader.stop()
    
    
class MovementReader(threading.Thread):
    
    def __init__(self, filename, nodes):
        threading.Thread.__init__(self)
        self.daemon=True
        self.filename = filename
        self.eof = False
        self.file = None
        self.buffer = None
        self.nodes = nodes
        
    def run(self):
        print("TheONE movement reader starting")
        self.running = True
        self.file = open(self.filename, 'r')
        
        ''' read the first line. it contains the min/max values for the area '''
        buffer = self.file.readline()
        
        ''' get min/max values '''
        (min_time, buffer) = buffer.split(" ", 1)
        (max_time, buffer) = buffer.split(" ", 1)
        (min_x, buffer) = buffer.split(" ", 1)
        (max_x, buffer) = buffer.split(" ", 1)
        (min_y, buffer) = buffer.split(" ", 1)
        (max_y, buffer) = buffer.split(" ", 1)
        
        ''' order all nodes beside the left border '''
        halign = float(max_x) * 1.1
        v_pos = float(max_y) * 0.025
        v_step = (float(max_y) * 0.975) / len(self.nodes)
        
        for n in self.nodes:
            n.x = halign
            n.y = v_step 
            v_step = v_pos + v_step
            n.updatePosition()
        
        ''' read the first data line '''
        self.readdata()
        
        ''' store the current time for comparison in the next round '''
        prevtime = self.currenttime
        
        ''' set disabled flag, we want to skip the movement trace until at least one node is not disabled '''
        disabled = True
        
        while not self.eof:
            ''' get the current node '''
            n = self.nodes[self.nodeid]
            
            ''' disable a node if it is out of range '''
            if self.x > 0 and self.y > 0:
                n.disabled = False
                disabled = False
                n.x = self.x
                n.y = self.y
                n.updatePosition()
            else:
                n.disabled = True
                
            if prevtime != self.currenttime:
                if not disabled:
                    time.sleep(self.currenttime - prevtime)
                print("Timestamp: " + str(self.currenttime))
                prevtime = self.currenttime
                
                ''' check all node connections '''
                self.updateConnections()
            
            ''' read the next line '''
            self.readdata()
        
        print("TheONE movement finished")
        
    def updateConnections(self):
        #print("Update Connections "+str(len(self.nodes)))
        for me in xrange(0,len(self.nodes)-1):
            for him in xrange(me+1,len(self.nodes)):
                if self.nodes[me].disabled:
                    self.nodes[me].disconnectFrom(self.nodes[him])
                    continue
                
                #print("Compare "+self.nodes[me].name+" with "+self.nodes[him].name)
                if self.nodes[me].distanceTo(self.nodes[him]) < self.nodes[me].range:
                    #print("Connect "+str(self.nodes[me].name)+" <-> "+str(self.nodes[him].name))
                    self.nodes[me].connectTo(self.nodes[him])
                else:
                    #print("Disconnect "+str(self.nodes[me].name)+" -/- "+str(self.nodes[him].name))
                    self.nodes[me].disconnectFrom(self.nodes[him])
        
    def readdata(self):
        buffer = self.file.readline().strip('\n')
        
        if (buffer == ''):
            self.eof = True
        else:
            ''' read the current timestamp '''
            (currenttime, buffer) = buffer.split(" ", 1)
            
            ''' read the node id '''
            (nodeid, buffer) = buffer.split(" ", 1)
            
            ''' read the x coordinate '''
            (x, buffer) = buffer.split(" ", 1)
            
            ''' read the y coordinate '''
            y = buffer
            
            ''' translate string values to numeric values '''
            self.currenttime = int(currenttime)
            self.nodeid = int(nodeid)
            self.x = float(x)
            self.y = float(y)
            
    def stop(self):
        print("TheONE movement reader stopping")
        self.running = False
        