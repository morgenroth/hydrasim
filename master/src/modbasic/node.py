'''
Created on 08.04.2010

@author: morgenro
'''

class BasicNode(object):
    '''
    classdocs
    '''

    def __init__(self, name, address):
        '''
        Constructor
        '''
        self.name = name
        self.address = address
        self.gateway = None
        self.netmask = None
        self.dns = None
        self.vhost = None
        self.ssh = None
        self.vhost = None
        
    def setup(self):
        self.ssh.execute("/usr/sbin/iptables -F") 
        self.ssh.execute("/usr/sbin/iptables -A OUTPUT -d " + self.gateway + "/32 -j ACCEPT") 
        self.ssh.execute("/usr/sbin/iptables -A OUTPUT -d " + self.dns + "/32 -j ACCEPT")
        self.ssh.execute("/usr/sbin/iptables -A OUTPUT -d 192.168.56.255/32 -j ACCEPT") 
        self.ssh.execute("/usr/sbin/iptables -A OUTPUT -d 255.255.255.255/32 -j ACCEPT")
        self.ssh.execute("/usr/sbin/iptables -A OUTPUT -d 127.0.0.1/8 -j ACCEPT")
        self.ssh.execute("/usr/sbin/iptables -A INPUT -s " + self.gateway + "/32 -j ACCEPT")
        self.ssh.execute("/usr/sbin/iptables -A INPUT -s " + self.dns + "/32 -j ACCEPT")
        self.ssh.execute("/usr/sbin/iptables -A INPUT -s 127.0.0.1/8 -j ACCEPT")
        self.ssh.execute("/usr/sbin/iptables -P OUTPUT DROP")
        self.ssh.execute("/usr/sbin/iptables -P INPUT DROP")
        pass
        
    def connectionUp(self, host):
        self.ssh.execute("/usr/sbin/iptables -A OUTPUT -d " + host.address + "/32 -j ACCEPT")
        self.ssh.execute("/usr/sbin/iptables -A INPUT -s " + host.address + "/32 -j ACCEPT")
        pass
        
    def connectionDown(self, host):
        self.ssh.execute("/usr/sbin/iptables -D OUTPUT -d " + host.address + "/32 -j ACCEPT")
        self.ssh.execute("/usr/sbin/iptables -D INPUT -s " + host.address + "/32 -j ACCEPT")
        pass
    
    def setDelay(self, host, delay, jitter):
        pass
    
    def setPacketLoss(self, host, loss):
        pass