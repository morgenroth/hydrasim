'''
Created on 29.03.2010

@author: morgenro
'''

import basics

def setupNat():
    print u"Please enter your SUDO password to enable NAT"
    basics.sudo("iptables -F")
    basics.sudo("iptables -F -t nat")
    basics.sudo("iptables -A POSTROUTING -t nat -o eth0 -j MASQUERADE")
    basics.sudo("iptables -A FORWARD -i vboxnet0 -o eth0 -j ACCEPT")
    basics.sudo("sysctl -w net.ipv4.ip_forward=1")
    
