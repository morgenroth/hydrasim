#! /usr/bin/python
# -*- coding: utf-8 -*-

# To change this template, choose Tools | Templates
# and open the template in the editor.
#
# 14.04.2010 adapt for i will not call it pyemulation


__author__="sebastianschildt"
__date__ ="$14.09.2009 14:29:02$"

from mobilitynode import MobilityNode
from logline import LogLine
import random
import math
import threading
import time


#TODO wraparound vs. turn


class RandomWalk(threading.Thread):
    """Random Walk Mobility"""
    def __init__(self, nodes, config):
        threading.Thread.__init__(self)
        self.daemon=True
        self.rand=random.Random()
        print("Initialize random walk  for "+str(len(nodes))+" nodes")

        #Creating mobility nodes
        self.nodes=[]
        for node in nodes:
            cn=MobilityNode(node)
            self.nodes.append(cn)

        self.filename   = config.get('randomwalk','tracefile')
        self.width      = config.getint('randomwalk', 'width')
        self.height     = config.getint('randomwalk','height')
        self.resolution = config.getint('randomwalk', 'resolution')
        self.movetime   = config.getint('randomwalk','movetime')
        self.vmin       = config.getfloat('randomwalk', 'vmin')
        self.vmax       = config.getfloat('randomwalk', 'vmax')
        self.range      = config.getfloat('randomwalk','range')

        if config.has_option('randomwalk', 'seed'):
            print("RandomWalk setting seed to "+str(config.getint('randomwalk', 'seed')))
            self.rand.seed(config.getint('randomwalk', 'seed'))




    def stop(self):
        print("Stopping random walk mobility model")
        self.running=False
        self.join()
        print("Random walk mobility model stopped")


    def run(self):
        print("Starting mobility model")
        currLog=LogLine();
        print("Open file for writing...")
        fout = open(self.filename, 'w')
        currLog.time=0

        #drop all nodes to random locations
        for node in self.nodes:
            currLog.node=node.name
            # @type node MobilityNode
            node.lasttime=0
            node.x=self.rand.uniform(0, self.width)
            node.y=self.rand.uniform(0,self.height)
            node.heading=self.rand.uniform(0,2*math.pi)
            node.speed=self.rand.uniform(self.vmin, self.vmax)
            currLog.position=(node.x,node.y)
            print("Generate start position for "+node.name)
            currLog.write_line(fout)

        
        absTime=0
        self.running=True
        while (self.running ):
            startTime=time.time()
            time.sleep(self.resolution)
            elapsedTime=time.time()-startTime
            absTime=absTime+elapsedTime

            for node in self.nodes:
                 dist=node.speed*(float(absTime)-float(node.lasttime))
                 #print("NodeID is "+str(node.name)+" and travels "+str(dist)+" (v: "+str(node[I_V])+" dT: "+str(float(time)-float(node.lasttime)))
                 dx=math.cos(node.heading)*dist
                 dy=math.sin(node.heading)*dist
                 nx=dx+node.x
                 ny=dy+node.y
                 #if out of bounds, turn 180deg
                 if nx < 0:
                     #print "B�MM L"
                     nx=0
                     node.heading  = (-math.pi-node.heading)%(2*math.pi)
                     node.x        =  nx #new basepoint
                     node.y        =ny #new basepoint
                     node.lasttime =absTime
                 elif nx > self.width:
                     #print "B�MM R"
                     nx=self.width
                     node.heading  =  (math.pi-node.heading)%(2*math.pi)
                     node.x        = nx #new basepoint
                     node.y        = ny #new basepoint
                     node.lasttime = absTime
                 if ny < 0:
                     #print "B�MM B"
                     ny            = 0
                     node.heading  =  (-2*math.pi-node.heading)%(2*math.pi)
                     node.y        = ny #new basepoint
                     node.x        = nx #new basepoint
                     node.lasttime = absTime
                 elif ny > self.height:
                     #print "B�MM T"
                     ny            = self.height
                     node.heading  = (2*math.pi-node.heading)%(2*math.pi)
                     node.y        = ny #new basepoint
                     node.x        = nx #new basepoint
                     node.lasttime = absTime
                #
                 currLog.time      = absTime
                 currLog.node      = node.name
                 currLog.position  = (nx,ny)
                 currLog.write_line(fout)
                 
                 #new basepoint reached (time elapsed)
                 if (absTime > node.lasttime+self.movetime):
                    #print "Switch direction"
                    node.heading   = self.rand.uniform(0,2*math.pi)
                    node.x         = nx #new basepoint
                    node.y         = ny #new basepoint
                    node.lasttime  = absTime
                    node.speed     = self.rand.uniform(self.vmin, self.vmax)
                    
                 """ write position to visualization """
                 node.updatePosition()
            #dddddd
            #Check connections
            self.updateConnections()
        fout.close()


    # O(0.5 n^2) :(
    def updateConnections(self):
        #print("Update Connections "+str(len(self.nodes)))
        for me in xrange(0,len(self.nodes)-1):
            for him in xrange(me+1,len(self.nodes)):
                #print("Compare "+self.nodes[me].name+" with "+self.nodes[him].name)
                if self.nodes[me].distanceTo(self.nodes[him]) < self.range:
                    #print("Connect "+str(self.nodes[me].name)+" <-> "+str(self.nodes[him].name))
                    self.nodes[me].connectTo(self.nodes[him])
                else:
                    #print("Disconnect "+str(self.nodes[me].name)+" -/- "+str(self.nodes[him].name))
                    self.nodes[me].disconnectFrom(self.nodes[him])


        

    def render(options):
        
        #steps=int(options.simtime/options.resolution)

        for time in xrange(options.resolution,options.simtime,options.resolution):
             print("Time "+str(time))
             





        #fout.write("HAI!")
        fout.close()


if __name__ == "__main__":
    (options, args)=parser.parse_args()
    print("Write trace to         : "+str(options.filename))
    print("Simulation area        : "+str(options.width)+"x"+str(options.height))
    print("Number of agents       : "+str(options.nodes))
    print("Simulate "+str(options.simtime)+" tu with a resolution of "+str(options.resolution)+ " tu/step leading to "+str(options.simtime/options.resolution)+" simulation steps.")
    print("Minimum agent velocity : "+str(options.vmin))
    print("Maximum agent velocity : "+str(options.vmax))
    print("Agent velocities will be uniformly distributed")
    print("Change direction after : "+str(options.movetime)+" tu")
    print("Random seed            : "+str(options.seed))
    random.seed(options.seed)
    render(options)






