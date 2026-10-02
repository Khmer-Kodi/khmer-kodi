LOGDEBUG,LOGINFO,LOGWARNING,LOGERROR=0,1,2,3
LOG=[]
def log(m,l=1): LOG.append(m)
BUILTINS=[]
def executebuiltin(*a): BUILTINS.append(a[0])
def getSkinDir(): return _os.environ.get("SKIN", "skin.estuary")
import os as _os
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
_orig_gcv = getCondVisibility
def getCondVisibility(cond):
    if cond.startswith("System.AddonIsEnabled("):
        return _os.environ.get("ISA_ENABLED", "0") == "1"
    return _orig_gcv(cond)

# JSON-RPC stub: Settings.Get/SetSettingValue backed by env FONTSET (default "Default").
import json as _json
RPC=[]
_SETTINGS={"lookandfeel.font": _os.environ.get("FONTSET", "Default")}
def executeJSONRPC(req):
    r=_json.loads(req); RPC.append(r); p=r.get("params",{})
    if r["method"]=="Settings.GetSettingValue": return _json.dumps({"id":1,"jsonrpc":"2.0","result":{"value":_SETTINGS.get(p["setting"])}})
    if r["method"]=="Settings.SetSettingValue": _SETTINGS[p["setting"]]=p["value"]; return _json.dumps({"id":1,"jsonrpc":"2.0","result":True})
    return _json.dumps({"id":1,"jsonrpc":"2.0","error":{"code":-32601}})
