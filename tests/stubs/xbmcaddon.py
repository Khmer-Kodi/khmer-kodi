import os
class Addon:
    _s={}
    def __init__(s,id=None): pass
    def getAddonInfo(s,k):
        if k=="path": return os.environ.get("ADDON_DIR",".")
        if k=="profile": return "special://profile/addon_data/plugin.video.KDubbed/"
        return "plugin.video.KDubbed"
    def getSetting(s,k): return Addon._s.get(k,"")
    def setSetting(s,k,v): Addon._s[k]=v
