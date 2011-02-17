
__author__="schildt"
__date__ ="$29.04.2010 14:05:02$"

import randomwalk
import logplay.theone
import movement.theone
from mobilitynode import MobilityNode

class MobilityModel:


    def __init__(self, setup):
        self.mobilitymodule= setup.config.get('mobility','model')
        if self.mobilitymodule == "randomwalk":
            self.model=randomwalk.RandomWalk(setup.ctrl.getNodes(), setup.config)
        elif self.mobilitymodule == "theone":
            self.model=logplay.theone.TheONEReader(setup.ctrl.getNodes(), setup.config)
        elif self.mobilitymodule == "static":
            self.model=logplay.static.StaticConnections(setup.ctrl.getNodes(), setup.config)
        elif self.mobilitymodule == "movement":
            #Creating mobility nodes
            mob_nodes = []
            for node in setup.ctrl.getNodes():
                cn = MobilityNode(node)
                mob_nodes.append(cn)
            
            self.model = movement.theone.Movement(mob_nodes, setup.setupdir, setup.config)
        else:
            print("Mobility: Unknown model "+str(self.mobilitymodule))
            self.start=self.nomodule
            self.stop=self.nomodule_stop

    def start(self):
        self.model.start()

    def stop(self):
        self.model.stop()


    def nomodule_start(self):
        print("Mobility: Can't start unknown mobility model "+str(self.mobilitymodule))

    def nomodule_stop(self):
        print("Mobility: Can't stop unknown mobility model "+str(self.mobilitymodule))