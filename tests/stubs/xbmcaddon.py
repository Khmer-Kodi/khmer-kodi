import os
class Addon:
    _s={}
    def __init__(s,id=None): pass
    def getAddonInfo(s,k): return os.environ.get("ADDON_DIR",".") if k=="path" else "plugin.video.KDubbed"
    def getSetting(s,k): return Addon._s.get(k,"")
    def setSetting(s,k,v): Addon._s[k]=v
