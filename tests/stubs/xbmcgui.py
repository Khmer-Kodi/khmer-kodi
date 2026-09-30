NOTIFICATION_ERROR="error"
DIALOGS=[]
class _Tag:
    def __init__(s): s.t=None
    def setTitle(s,t): s.t=t
class ListItem:
    def __init__(s,label="",path=""): s.label,s.path,s.props,s.tag=label,path,{},_Tag()
    def setArt(s,a): pass
    def getVideoInfoTag(s): return s.tag
    def setProperty(s,k,v): s.props[k]=v
    def setContentLookup(s,v): pass
    def setMimeType(s,m): pass
    def setInfo(s,*a,**k):
        import warnings; DIALOGS.append("DEPRECATED setInfo used")
class Dialog:
    def ok(s,*a): DIALOGS.append(("ok",)+a)
    def select(s,h,l): return 0
    def notification(s,*a): DIALOGS.append(("notify",)+a)
    def textviewer(s,*a): pass
def _noop(*a,**k): pass
for _n in ("setPath","setLabel2","addContextMenuItems","setIsFolder","setSubtitles","setCast","setPlot","setGenres","setYear","setMediaType","setUniqueIDs","setRating","setDuration","setEpisode","setSeason","setTvShowTitle","setPremiered"):
    setattr(ListItem,_n,_noop); setattr(_Tag,_n,_noop)
NOTIFICATION_WARNING="warning"; NOTIFICATION_INFO="info"
