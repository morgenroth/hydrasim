'''
Created on 14.02.2011

@author: morgenro
'''

import SocketServer
import socket
import threading
from sets import Set

_vizserver = None

class VizServerHandler(SocketServer.BaseRequestHandler):
    
    def setup(self):
        print("viz connection opened (" + self.client_address[0] + ":" + str(self.client_address[1]) + ")")
        _vizserver.connections.add(self)

    def finish(self):
        print("viz connection closed (" + self.client_address[0] + ":" + str(self.client_address[1]) + ")")
        _vizserver.connections.remove(self)

    def handle(self):
        """ get all positions """
        for key, n in _vizserver.nodes.items():
            self.request.send(key + ";" + str(n[0]) + ";" + str(n[1]) + ";" + str(n[2]) + ";\n")
        
        self.request.recv(1500)
        
class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True

class VizServer(object):
    
    def __init__(self, address):
        self.address = address
        self.nodes = { }
        self.connections = Set()
    
    def startup(self):
        global _vizserver
        _vizserver = self
        
        self.server = ThreadedTCPServer(self.address, VizServerHandler)
    
        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        # Exit the server thread when the main thread terminates
        self.server_thread.setDaemon(True)
        self.server_thread.start()
        print "Server loop running in thread:", self.server_thread.getName()
        
    def shutdown(self):
        self.server.shutdown()
    
    def nodePosition(self, name, x, y, z):
        self.nodes[name] = (x, y, z)
        
        for c in self.connections:
            c.request.send(name + ";" + str(x) + ";" + str(y) + ";" + str(z) + ";\n")
        
        print("position of " + name + " " + str(x) + " x " + str(y) + " x " + str(z))

