# To change this template, choose Tools | Templates
# and open the template in the editor.

from mobility.logplay.player import ConnectionPlayer
from mobility.mobilitynode import MobilityNode

__author__="schildt"
__date__ ="$28.04.2010 17:24:33$"


class TheONEReader:
    def __init__(self, nodes, config):
        self.file = config.get('onetrace','file')
        self.f=open(self.file,'r')
        oneNodes=[]
        for node in nodes:
            cn=MobilityNode(node)
            oneNodes.append(cn)

        self.player=ConnectionPlayer(oneNodes,self)


    def start(self):
        self.player.start()

    def stop(self):
        self.player.stop()

    def __iter__(self):
        return self

    def next(self):
        while (True):
            line=self.f.readline()
            if line=="":
                raise StopIteration
            parts=line.split()
            if len(parts) != 4:
                continue
            if parts[2] == "DOWN":
                direction=0
            elif parts[2] == "UP":
                direction=1
            else:
                continue
            timestamp=int(float(parts[0][:-1]))
            n1=int(parts[3][1:parts[3].find("<")])
            n2=int(parts[3][parts[3].rfind(">")+2:])
            return (timestamp, direction, n1,n2)


