'''
Created on 19.01.2011

@author: morgenro
'''

import SimpleHTTPServer
import SocketServer
from optparse import OptionParser
import os

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

    print "serving at port", port
    httpd.serve_forever()