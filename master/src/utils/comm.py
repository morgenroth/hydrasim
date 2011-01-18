'''
Created on 08.04.2010

@author: morgenro
'''

import threading
import socket

class PHOperator(threading.Thread):
    '''
    classdocs
    '''
    
    def __init__(self, count):
        threading.Thread.__init__(self)
        self.count = count
        self.lock = threading.Lock()

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 9483))
        s.listen(1)
        
        while self.count > 0:
            conn, addr = s.accept()
        
            print("Connected by " + str(addr))
            
            while 1:
                data = conn.recv(1024)
                if not data:
                    break
            
            self.lock.acquire()
            self.count = self.count - 1
            self.lock.release()
            
            conn.close()
            
            if self.count <= 0:
                break
            
    def getCount(self):
        return self.count