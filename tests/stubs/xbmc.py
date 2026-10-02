LOGDEBUG,LOGINFO,LOGWARNING,LOGERROR=0,1,2,3
LOG=[]
def log(m,l=1): LOG.append(m)
def executebuiltin(*a): pass
class Keyboard:
    def __init__(s,*a): pass
    def setHeading(s,*a): pass
    def doModal(s): pass
    def isConfirmed(s): return True
    def getText(s): return "love"
import os as _os
def getCondVisibility(cond):
    if cond.startswith("System.HasAddon("):
        return _os.environ.get("YT_INSTALLED", "1") == "1"
    return False
