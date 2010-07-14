__author__="schildt"
__date__ ="$05.05.2010 14:02:51$"

from modsmokeping.controller import SmokepingController

def getController(setupdir, config):
    return SmokepingController(setupdir, config)
