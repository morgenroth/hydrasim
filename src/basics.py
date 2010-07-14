'''
Created on 08.04.2010

@author: morgenro
'''
import threading
import traceback

import time
from utils import ssh, iptables
from utils.comm import PHOperator
from vbox import master
import ConfigParser
import sys
import os

import shutil

# global configuration
gconfig = None
masters = None

def setMasterNodes(masters, nodes):
    # get the first master
    current_master = int(-1)
    nodesleft = int(0)

    for n in nodes:
        try:
            while nodesleft == 0:
                current_master = current_master + 1
                maxnodes = masters[current_master].options["maxnodes"]
                if maxnodes != None:
                    nodesleft = int(maxnodes)
                else:
                    nodesleft = -1

            nodesleft = nodesleft - 1
            
            n.vmaster = masters[current_master]
            n.vhost.master = n.vmaster
        except IndexError:
            n.vmaster = None
            n.vhost.master = None

def prepareSimulation(datadir, tmpdir, setupdir, config, ctrl):
    global gconfig, masters
    
    # set the global config
    gconfig = config
    
    # create a local masterhost
    masters = master.getVBoxMasters(config, datadir, setupdir, tmpdir)

    # get filename of the base image
    if config.get('domu', 'image')[0] == '/':
        baseimage=config.get('domu', 'image')
    else:
        baseimage = setupdir + "/" + config.get('domu', 'image')

    # run basic setup
    prototype = baseSetup(baseimage, datadir, tmpdir, setupdir)
    
    # assign a master to each node
    nodes = ctrl.getNodes()
    setMasterNodes(masters, nodes)
    
    # setup all nodes
    for node in nodes:
        nodeSetup(node, prototype, datadir, setupdir)

    for m in masters:
        m.commit()


def cleanSimulation(config, ctrl, datadir, tmpdir, setupdir):
    global gconfig, masters
    
    # set the global config
    gconfig = config

    # create a local masterhost
    masters = master.getVBoxMasters(config, datadir, setupdir, tmpdir)
    
    # assign a master to each node
    nodes = ctrl.getNodes()
    setMasterNodes(masters, nodes)
    
    cleanUp(nodes)


def runSimulation(datadir, tmpdir, setupdir, config, ctrl):
    try:
        _runSimulation(datadir, tmpdir, setupdir, config, ctrl)
    except Exception as exp:
        print("********************* Something bad happend ************************")
        print("The problem: "+str(exp))
        traceback.print_exc()
        print("Trying to clean up the mess....")
        cleanSimulation(config,ctrl,datadir,tmpdir,setupdir)
    except KeyboardInterrupt:
        print("Keyboard Strg-C")
        print("Trying to clean up....")
        cleanSimulation(config,ctrl,datadir,tmpdir,setupdir)
        

def _runSimulation(datadir, tmpdir, setupdir, config, ctrl):
    global gconfig, masters
    
    # set the global config
    gconfig = config
    
    # create a local masterhost
    masters = master.getVBoxMasters(config, datadir, setupdir, tmpdir)
    
    # setup NAT if requested
    try:
        if config.get('dom0', 'nat') == "1":
            print("setup network address translation")
            iptables.setupNat()
    except ConfigParser.NoOptionError:
        pass
    
    # assign a master to each node
    nodes = ctrl.getNodes()
    setMasterNodes(masters, nodes)
    
    # create VMs for all nodes
    numberofnodes = 0
    print("setup virtual machines...")
    for node in nodes:
        createVM(node)
        if node.vmaster != None:
            numberofnodes = numberofnodes + 1
    
    # set host ip address
    try:
        masters[0].setVBox0IP(config.get('dom0', 'address'))
    except ConfigParser.NoOptionError:
        pass
    
    
    # get a listener for machine callback
    op = PHOperator(numberofnodes)
    op.start()
    
    # run all VMs
    print("Run virtual machines...")
    for node in nodes:
        node.vhost.start()

    # commit command execution
    for m in masters:
	m.commit()
        
    # wait for all machine callbacks foor max 10 min
    #TODO: Make configurable?
    print("Waiting for nodes....")
    op.join(600)
    if op.isAlive():
        print("Not all machines registered with the controller")
        print("Trying a cleanup")
        cleanUp(nodes)
        sys.exit(-12)

    print("All nodes registered with controller. Connecting nodes...")

    # setup ssh connections to all hosts
    for node in nodes:
        if node.vmaster != None:
            while node.ssh == None:
                try:
                    node.ssh = ssh.RemoteHost(node.address, "root", None, datadir + "/" + node.sshkey)
                    node.ssh.connect()
                    node.setup()
                except:
                    # connection failed or refused
                    print("SSH connection failed, reconnecting...")
                    time.sleep(1)
                    node.ssh = None

    # run custom simulation
    ctrl.run()
    ctrl.shutdown()
    # collect files of the nodes
    try:
        files = config.get("download", "files").split(" ")
        
        # create the download directory
        os.mkdir(tmpdir + "/download")
        
        for node in nodes:
            if node.vmaster != None:
                try:
                    # create a directory
                    os.mkdir(tmpdir + "/download/" + node.name)
                    
                    for f in files:
                        node.ssh.get(f, tmpdir + "/download/" + node.name + "/")
                except:
                    print("downloading of files failed on node " + node.name)
    except:
        pass
    
    # clean up the simulation
    cleanUp(nodes)
    
    
def cleanUp(nodes):
    # close all VMs
    print("Closing virtual machines...")
    for node in nodes:
        if node.ssh != None:
            node.ssh.execute("/sbin/halt")
            time.sleep(1)
            node.ssh.close()

    # wait some time
    time.sleep(4)

    # stop all virtual machines
    for node in nodes:
        node.vhost.stop()
        node.vmaster.commit()
    
    # wait some time
    time.sleep(4)
    
    # delete all VMs
    sys.stdout.write("remove virtual machines...")
    for node in nodes:
        sys.stdout.write(" [" + node.name + "]")
        sys.stdout.flush()
        removeVM(node)
        
    sys.stdout.write("\n")
    sys.stdout.flush()


def sudo(command):
    global gconfig
    if gconfig.get('general', 'sudoquote') == "1":
        os.system(gconfig.get('general', 'sudocmd') +" '"+str(command)+"'")
    else:
        os.system(gconfig.get('general', 'sudocmd') +" "+str(command))

#Set up base
def baseSetup(baseimage, datadir, tmpdir, setupdir):
    print("Copying base image....")
    prototype_image = tmpdir + "/prototype.image"
    shutil.copy(baseimage, prototype_image)
    
    print("Basic image preparation")
    sudo("/bin/bash " + datadir + "/prepare_image_base.sh " + prototype_image + " " + setupdir)
    
    # copy the prepares image to all ssh masters
    global masters
    for m in masters:
        if m.options["type"] != "local":
            m.upload(prototype_image)

    
    return prototype_image

def nodeSetup(node, prototype, datadir, setupdir):
    if node.vmaster == None:
        print("Skip setup of node " + node.name + "; No resources left.")
        return
    
    print("Setup node " + node.name)
    
    # get the master for this node
    vmaster = node.vmaster
    
    # upload needed scripts
    vmaster.upload(setupdir + "/modify_image_node.sh")
    vmaster.upload(datadir + "/prepare_image_node.sh")
    vmaster.upload(datadir + "/magicmount.sh")
    vmaster.execute("mkdir -p " + vmaster.options["tmpdir"] + "/mnt")
    
    vmaster.upload(datadir + "/" + node.sshpubkey)
    sshkey = os.path.basename(node.sshpubkey)
    
    # copy the prototype to a new image
    vmaster.copy(vmaster.options["tmpdir"]+"/prototype.image", vmaster.options["tmpdir"]+"/"+node.image)
    
    # run prepare script
    vmaster.sudo("bash " + vmaster.options["tmpdir"] + "/prepare_image_node.sh " + vmaster.options["tmpdir"]+"/"+node.image + " " + vmaster.options["tmpdir"] + " " + node.address + " " + node.name + " " + node.gateway + " " + node.dns + " " + sshkey)
    
    # remove old vdi image
    try:
        vmaster.remove(vmaster.options["tmpdir"]+"/"+node.vdiimage)
    except OSError:
        pass
    
    # create new vdi image
    vmaster.createHD(vmaster.options["tmpdir"]+"/"+node.image, vmaster.options["tmpdir"]+"/"+node.vdiimage)
    
    # remove the node image
    vmaster.remove(vmaster.options["tmpdir"]+"/"+node.image)


def createVM(node):
    if node.vmaster == None:
        print("Skip creating of node " + node.name + "; No resources left.")
        return
    
    print("Creating VM " + node.name)
    node.vmaster.createVM(node.name)
    node.vmaster.configWith(node.name, node.vboxopts)
    node.vmaster.connectHd(node.name, node.vmaster.options["tmpdir"]+"/"+node.vdiimage)
    

def removeVM(node):
    if node.vmaster == None:
        return
    print("Removing VMs")
    node.vhost = None
    node.vmaster.unregisterVM(node.name)
    node.vmaster.removeImage(node.vmaster.options["tmpdir"]+"/"+node.vdiimage)

def exit():
    for m in masters:
        m.close()
