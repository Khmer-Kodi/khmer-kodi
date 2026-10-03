import os, json
# Per-add-on settings; env YT_FEATURES_JSON seeds plugin.video.youtube's stream features.
_STORE = {}
SETCALLS = []
class Settings:
    def __init__(s, aid): s.aid = aid
    def getStringList(s, k):
        d = _STORE.setdefault(s.aid, {})
        if k not in d and s.aid == "plugin.video.youtube" and os.environ.get("YT_FEATURES_JSON"):
            d[k] = json.loads(os.environ["YT_FEATURES_JSON"])
        return list(d.get(k, []))
    def setStringList(s, k, v): _STORE.setdefault(s.aid, {})[k] = list(v); SETCALLS.append((s.aid, k, list(v)))
class Addon:
    _s={}
    def __init__(s,id=None): s.id = id or "plugin.video.KDubbed"
    def getAddonInfo(s,k):
        if k=="path": return os.environ.get("ADDON_DIR",".")
        if k=="profile": return f"special://profile/addon_data/{s.id}/"
        return s.id
    def getSetting(s,k): return Addon._s.get(k,"")
    def setSetting(s,k,v): Addon._s[k]=v
    def getSettings(s): return Settings(s.id)
