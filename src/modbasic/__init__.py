#
# basic simulation module
#

from modbasic.controller import BasicController

def getController(setupdir, config):
    return BasicController(setupdir, config)
