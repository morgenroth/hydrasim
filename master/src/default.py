#!/usr/bin/python
#
# Run simulation
# (c) 2010 IBR

import sys
import ConfigParser
from basics import Setup
from optparse import OptionParser
import webserver
import time
import os

def _run_webserver(datadir):
    websrv = webserver.Webserver(8080)
    websrv.start()

if __name__ == '__main__':
    print("- hydra emulation 0.2 -")
    
    """ help message """
    usage = "usage: %prog [options] clean|prepare|run|all [setupname]"
    
    """ instance a option parser """
    parser = OptionParser(usage=usage)
    
    """ add options to the parser """
    parser.add_option("-t", "--tmp-dir", dest="tmpdir", default="/tmp",
        help="define a temporary directory")
    parser.add_option("-d", "--data-dir", dest="datadir", default="../data",
        help="specify the data directory containing setup scripts and ssh keys")

    """ parse arguments """
    (options, args) = parser.parse_args()
    
    """ change to an absolute path of tmpdir and datadir """
    options.tmpdir = os.path.abspath(options.tmpdir)
    options.datadir = os.path.abspath(options.datadir)
    
    """ change into the datadir as working directory """
    os.chdir(options.datadir)
    
    """ get runmode """
    try:
        runmode = args[0]
    except IndexError:
        parser.error("Run mode not specified. Please choose one of 'clean', 'prepare', 'run' or 'all'.")
    
    """ get setup name """
    try:
        setupname = args[1]
    except IndexError:
        print("Name of setup missing! Using 'default'.")
        setupname = "default"
        
    # define setup directory
    setupdir = options.datadir + "/setups/" + setupname
    
    """ read configuration """
    config = ConfigParser.RawConfigParser()
    print("read configuration: " + setupdir + "/config.properties")
    config.read(setupdir + "/config.properties")
    modulename = config.get('general','module')
    if modulename == None:
        print("Module not specified in " + setupdir + "/config.properties.")
        sys.exit(-1)

    """ create a new setup """
    s = Setup(config, setupname, options.datadir)
    
    try:
        if runmode == "prepare":
            _run_webserver(options.datadir)
            s.prepare()
        elif runmode == "run":
            s.run()
        elif runmode == "clean":
            s.cleanup()
        elif runmode == "all":
            _run_webserver(options.datadir)
            s.prepare()
            s.run()
        else:
            print("Invalid runmode "+str(runmode))
            sys.exit(-1)
    finally:
        s.exit()
        
    print("Done")
