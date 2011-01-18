from time import sleep
import time
import threading

__author__="schildt"
__date__ ="$28.04.2010 14:24:32$"



class ConnectionPlayer(threading.Thread):
    def __init__(self, nodes, reader):
        threading.Thread.__init__(self)
        self.daemon=True
        self.nodes=nodes
        #hashmap of node names
        self.nodemap={}
        for node in self.nodes:
            self.nodemap[node.name]=node
        self.reader=reader

    def stop(self):
        print("Connection player stopping")
        self.running=False
        #No need to join: Python can't interrupt the thread so a sleep might stall
        #for a long time. As this thread is daemonic, it is automatically killed
        #the flag prevents it from executing any further actions on nodes
        pass
      
    def run(self):
        self.running=True
        self.startTime=time.time()
        for event in self.reader:
            currTime=time.time()-self.startTime
            if currTime < event[0]:
                sleep(event[0]-currTime)
            if not self.running:
                break
            print("Con "+str(event))
            dir=event[1]
            node1=str(event[2])
            node2=str(event[3])
            if  node1 not in self.nodemap or node2 not in self.nodemap:
                print(" ->Skip, node not included in simulation")
                continue
            else:
                if dir == 1: #UP
                    self.nodemap[node1].connectTo(self.nodemap[node2], True)
                else: #DOWN
                    self.nodemap[node1].disconnectFrom(self.nodemap[node2], True)
        print("ConnectionPlayer finished")





class PositionPlayer:
    def __init__(self):
        pass