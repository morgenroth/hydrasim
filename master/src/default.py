#!/usr/bin/python
#
# Run simulation
# (c) 2010 IBR

import sys
import ConfigParser
import basics
from optparse import OptionParser

if __name__ == '__main__':
    print("- pyEmulation 0.1 -")
    
    usage = "usage: %prog [options] clean|prepare|run|all [setupname]"
    parser = OptionParser(usage=usage)
#    parser.add_option("-m", "--max-nodes", dest="maxnodes", default=0,
#        help="create max. X nodes and ignore the rest")
#    parser.add_option("-s", "--setup", action="store_true", dest="setup",
#                      help="Do a prototype setup before the simulation starts.")
#    parser.add_option("-r", "--run", action="store_true", dest="run",
#                      help="Run the simulation.")
    parser.add_option("-t", "--tmp-dir", dest="tmpdir", default="/tmp",
        help="define a temporary directory")
    parser.add_option("-d", "--data-dir", dest="datadir", default="../data",
        help="specify the data directory containing setup scripts and ssh keys")

    # parse arguments
    (options, args) = parser.parse_args()
    
    # get runmode
    try:
        runmode = args[0]
    except IndexError:
        parser.error("Run mode not specified. Please choose one of clean|prepare|run|all.")
    
    # get setup name
    try:
        setupname = args[1]
    except IndexError:
        print("Name of setup missing! Using 'default'.")
        setupname = "default"
    
    # define setup directory
    setupdir = options.datadir + "/setups/" + setupname
        
    # read configuration
    config = ConfigParser.RawConfigParser()
    print("read configuration: " + setupdir + "/config.properties")
    config.read(setupdir + "/config.properties")
    modulename = config.get('general','module')
    if modulename == None:
        print("Module not specified in " + setupdir + "/config.properties.")
        sys.exit(-1)
    
    # import the module
    ctrl = None
    exec("import " + modulename)
    exec("ctrl = " + modulename + ".getController(setupdir, config)")

    if runmode == "prepare":
        basics.prepareSimulation(options.datadir, options.tmpdir, setupdir, config, ctrl)
    elif runmode == "run":
        basics.runSimulation(options.datadir, options.tmpdir, setupdir, config, ctrl)
    elif runmode == "clean":
        basics.cleanSimulation(config, ctrl, options.datadir, options.tmpdir, setupdir)
    elif runmode == "all":
        basics.prepareSimulation(options.datadir, options.tmpdir, setupdir, config, ctrl)
        basics.exit();
        basics.runSimulation(options.datadir, options.tmpdir, setupdir, config, ctrl)
    else:
        print("Invalid runmode "+str(runmode))
        sys.exit(-1)

    basics.exit();
    print("Done")
