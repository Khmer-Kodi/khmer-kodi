import sys, os, runpy, types, requests, importlib
HERE=os.path.dirname(os.path.abspath(__file__))
addon_dir, action, url, scenario = sys.argv[1:5]
if scenario=="no_youtube": os.environ["YT_INSTALLED"]="0"
if scenario=="isa_on": os.environ["ISA_ENABLED"]="1"
sys.path[:0]=[os.path.join(HERE,"stubs"), addon_dir]; os.environ["ADDON_DIR"]=addon_dir
PAGES = {
 "tk_eps_okru":open(os.path.join(HERE,"fixtures","tk_eps_okru.html")).read(),
 "tk_eps_rumble":open(os.path.join(HERE,"fixtures","tk_eps_rumble.html")).read(),
 "kk_eps":open(os.path.join(HERE,"fixtures","kk_eps.html")).read(),
 "kk_listing":open(os.path.join(HERE,"fixtures","kk_listing.html")).read(),
 "mk_eps":open(os.path.join(HERE,"fixtures","mk_eps.html")).read(),
 "mk_listing":open(os.path.join(HERE,"fixtures","mk_listing.html")).read(),
 "kan_eps":open(os.path.join(HERE,"fixtures","kan_eps.html")).read(),
 "kan_listing":open(os.path.join(HERE,"fixtures","kan_listing.html")).read(),
 "v4listing":open(os.path.join(HERE,"fixtures_v4","listing.html")).read(),
 "v4eps":open(os.path.join(HERE,"fixtures_v4","episodes.html")).read(),
 "v4single":open(os.path.join(HERE,"fixtures_v4","single.html")).read(),
 "craft":'<a href="https://www.craft4u.top/myshow-01/">1</a><a href="https://www.craft4u.top/myshow-03/">3</a>',
 "playerlist":'<html><script>options.player_list = [{"file":"https://x.com/a.mp4","title":"Episode 2"},{"file":"https://ok.ru/video/1","title":"Episode 1"}];</script></html>',
 "constvideos":"<html><script>const videos = [{file:'https://www.ckh7.com/v1.mp4', title:'Ep 1'},];</script></html>",
}
class R:
    def __init__(s,t,c=200): s.text,s.content,s.status_code,s.url=t,t.encode(),c,"u"
    def raise_for_status(s):
        if s.status_code>=400: raise requests.HTTPError(f"HTTP {s.status_code}")
FX2=os.path.join(HERE,"fixtures")+"/"
URLMAP=[("livetv.json",FX2+"livetv.json"),("rumble.com/embedJS",FX2+"rumble_api.json"),("feeds/posts/default",FX2+"tk_feed.json")]
def fake_get(self,u,**k):
    if scenario=="urlmap":
        for key,f in URLMAP:
            if key in u: return R(open(f).read())

    if scenario=="neterror": raise requests.ConnectionError("simulated outage")
    return R(PAGES.get(scenario,"<html></html>"))
requests.Session.get=fake_get
# Fake YouTube web API (youtubei/v1/browse): picks a fixture from the request body.
import json as _json
POSTS=[]
def fake_post(self,u,data=None,**k):
    if scenario=="neterror": raise requests.ConnectionError("simulated outage")
    b=_json.loads(data or "{}"); POSTS.append(b)
    if "youtubei/v1/browse" not in u: return R("{}",404)
    cont=b.get("continuation",""); bid=b.get("browseId",""); par=b.get("params","")
    if cont: name={"PLAYLISTS_PAGE2_TOKEN":"yt_channel_playlists_next","PLAYLIST_PAGE2_TOKEN":"yt_playlist_next","VIDEOS_PAGE2_TOKEN":"yt_channel_videos_next"}.get(cont)
    elif bid.startswith("VL"): name="yt_playlist_long" if bid=="VLUULONG" else "yt_playlist"
    elif par=="EglwbGF5bGlzdHPyBgQKAkIA": name="yt_channel_playlists"
    elif par=="EgZ2aWRlb3PyBgQKAjoA": name="yt_channel_videos"
    else: name=None
    if not name: return R("{}",400)
    return R(open(FX2+name+".json",encoding="utf-8").read())
requests.Session.post=fake_post
class _H:
    def __init__(s,u): s.url=u
requests.head=lambda u,**k: _H("https://vod.example.com/ep03.mp4/manifest.m3u8" if "tinyurl" in u else u)
sys.argv=["plugin://plugin.video.KDubbed/","1",f"?action={action}&url={requests.utils.quote(url,safe='')}"]
import xbmcplugin, xbmcgui
try:
    runpy.run_path(os.path.join(addon_dir,os.environ.get("ENTRY","ADDON.py")), run_name="__main__"); status="OK"
except Exception as e: status=f"CRASH {type(e).__name__}: {e}"
import os as _o
if _o.environ.get("VERBOSE") and getattr(xbmcplugin,"RESOLVED_PROPS",None): print("    props:",xbmcplugin.RESOLVED_PROPS[0])
if _o.environ.get("VERBOSE"):
    import urllib.parse as up
    for l,u,f in xbmcplugin.ITEMS: q=dict(up.parse_qsl(u.split("?",1)[1])) if "?" in u else {"action":"(link)","url":u}; print("   ",l,"|",q.get("action"),"|",q.get("url","")[:95],"|",q.get("icon","")[:70])
if _o.environ.get("DUMP"):
    import xbmc as _x; print("VIEW",_json.dumps({"builtins":_x.BUILTINS,"content":xbmcplugin.CONTENT,"rpc":_x.RPC,"dialogs":[list(d) for d in xbmcgui.DIALOGS],"addon_settings":__import__("xbmcaddon").SETCALLS}))
if _o.environ.get("DUMP"): print("ITEMS",_json.dumps(xbmcplugin.ITEMS)); print("POSTS",_json.dumps(POSTS))
print(f"{status} | ended={len(xbmcplugin.ENDS)} | items={len(xbmcplugin.ITEMS)} {[i[0] for i in xbmcplugin.ITEMS][:4]} | resolved={xbmcplugin.RESOLVED[:1]} | dialogs={[d for d in xbmcgui.DIALOGS][:2]}")
