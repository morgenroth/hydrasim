#!/usr/bin/python
#
# Run simulation
# (c) 2010 IBR

import sys
import ConfigParser
from basics import Setup
from optparse import OptionParser

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
    
    if runmode == "prepare":
        s.prepare()
    elif runmode == "run":
        s.run()
    elif runmode == "clean":
        s.cleanup()
    elif runmode == "all":
        s.prepare()
        s.run()
    else:
        print("Invalid runmode "+str(runmode))
        sys.exit(-1)

    s.exit()
    print("Done")
