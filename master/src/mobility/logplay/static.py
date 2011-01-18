# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="schildt"
__date__ ="$30.04.2010 15:13:40$"

from mobility.logplay.player import ConnectionPlayer
from mobility.mobilitynode import MobilityNode

class StaticConnections:

    def __init__(self,nodes,config):
        self.f = open(config.get('staticconnections','connections'))
        self.staticnodes=[]
        for node in nodes:
            cn=MobilityNode(node)
            self.staticnodes.append(cn)

        self.player=ConnectionPlayer(self.staticnodes,self)

    def start(self):
        self.player.start()

    def stop(self):
        self.player.stop()
        
    def __iter__(self):
        return self

    def next(self):
        parts = []
        while len(parts) != 3:
            line=self.f.readline()
            if line=="":
                raise StopIteration
            parts=line.split()
        direction = int(parts[2])
        return (0, direction, int(parts[1]),int(parts[2]))