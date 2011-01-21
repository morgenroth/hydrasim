'''
Created on 19.01.2011

@author: morgenro
'''

import SimpleHTTPServer
import SocketServer
from optparse import OptionParser
import os
import threading

if __name__ == '__main__':
    """ help message """
    usage = "usage: %prog <port> <path>"
    
    """ instance a option parser """
    parser = OptionParser(usage=usage)
    
    """ parse arguments """
    (options, args) = parser.parse_args()
    
    #ip = args[0]
    port = int(args[0])
    path = args[1]
    os.chdir(path)
    handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", port), handler)

    try:
        print "serving at port", port
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    
class Webserver(threading.Thread):
    
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.daemon = True
        self.port = port
    
    def run(self):
        handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        httpd = SocketServer.TCPServer(("", self.port), handler)
    
        print "http serving at port", self.port
        httpd.serve_forever()
