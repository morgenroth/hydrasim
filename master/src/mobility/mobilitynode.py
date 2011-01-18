# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="sebastianschildt"
__date__ ="$25.09.2009 10:08:19$"

import math



class MobilityNode:

    def __init__(self,modelnode):
        self.modelnode=modelnode
        # @type modelnode modbasic.node
        self.name=modelnode.name
        self.x=self.y=self.heading=self.speed=0
        self.currentConnections=[]

    @property
    def x(self):
        return self.ix

    @x.setter
    def x(self,x):
        self.ix=float(x)

    @property
    def y(self):
        return self.iy

    @y.setter
    def y(self,y):
        self.iy=float(y)


    @property
    def name(self):
        return self.name


    @property
    def heading(self):
        return self.heading

    @heading.setter
    def heading(self,heading):
        self.heading=float(heading)


    @property
    def speed(self):
        return self.speed

    @speed.setter
    def speed(self,speed):
        self.heading=float(speed)


    @property
    def lasttime(self):
        return self.lasttime

    @lasttime.setter
    def lasttime(self,lasttime):
        self.lasttime=float(lasttime)

    def connectTo(self, othernode, backconnection=True):
        if othernode.name not in self.currentConnections:
            self.currentConnections.append(othernode.name)
            self.modelnode.connectionUp(othernode.modelnode)
            if backconnection:
                othernode.connectTo(self, False)

    def disconnectFrom(self,othernode,backdisconnect=True):
        if othernode.name in self.currentConnections:
            self.currentConnections.remove(othernode.name)
            self.modelnode.connectionDown(othernode.modelnode)
            if backdisconnect:
                othernode.disconnectFrom(self, False)

    def distanceTo(self,othernode):
        return math.sqrt( float((othernode.x-self.x)*(othernode.x-self.x)) + float((othernode.y-self.y)*(othernode.y-self.y))    )
        
