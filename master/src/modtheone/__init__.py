#
# theone simulation module
#

import sys
from modtheone.controller import TheOneController

def getController(setupdir, config):
    filename = setupdir + "/" + config.get('modtheone', 'logfile')
    
    if filename == None:
        print("Log-filename missing! Please specify it in the configuration file.")
        sys.exit(-1)
    
    return TheOneController(setupdir, config)
