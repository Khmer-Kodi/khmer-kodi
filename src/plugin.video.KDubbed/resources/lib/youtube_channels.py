# ────────────────────────────────────────────────
#  YOUTUBE CHANNELS
#  Listings (playlists, videos, pages) come straight from YouTube's public web
#  API, so no personal API key is needed. Playback is handed to Kodi's official
#  YouTube add-on (plugin.video.youtube/play/?video_id=...), which also works
#  without API keys.
#
#  Why: the YouTube add-on's own channel/playlist pages use the YouTube Data API,
#  which now refuses to work without the user's own API keys ("The YouTube
#  add-on now requires that you use your own API keys").
#
#  To add a channel: append (name, channel_id) to CHANNELS. The single
#  "YouTube Channels" menu entry lists them all automatically.
# ────────────────────────────────────────────────
import re, json, requests, xbmc, xbmcgui, xbmcplugin
from resources.lib import sitekit as kit

YOUTUBE_ADDON = "plugin.video.youtube"
PLAY_URL = f"plugin://{YOUTUBE_ADDON}/play/?video_id={{}}"

API_URL = "https://www.youtube.com/youtubei/v1/browse?prettyPrint=false"
CLIENT_VERSION = "2.20261002.01.00"   # YouTube web client version (refresh if YouTube rejects it)
TAB_PLAYLISTS = "EglwbGF5bGlzdHPyBgQKAkIA"
TAB_VIDEOS = "EgZ2aWRlb3PyBgQKAjoA"
CONT = "cont:"                         # url prefix for "next page" continuation tokens
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/137.0 Safari/537.36")

# (display name, YouTube channel ID "UC...")
CHANNELS = [
    ("TVB Cambodia Drama", "UCAbHU5C61UNjwPV8MF5b2Bg"),   # youtube.com/@TVB_Cambodia
    ("Hang Meas Khmer Drama", "UCd6StwIVjo8Zu4M4JAAFiSQ"),  # youtube.com/@HangMeasKhmerDramaOfficial
    ("Hang Meas HDTV", "UCm1syRy-B1uAkeecQS_2I3w"),         # youtube.com/@HMHDTV-Official
    ("Rasmey Hang Meas", "UCHwYHdX37UUt6d9e1wAp9Bw"),       # youtube.com/@HangMeasVideos (music)
    ("TVB Cambodia - Romance & Comedy", "UCp49cPgy5z2eTvE-kxtchrg"),  # youtube.com/@TVBCambodia-RomanceComedy
    ("Cambodian Idol", "UC8b-bkP65mcy4wMFEw3eirw"),         # youtube.com/@MyChannel-u7c
    ("PPCTV", "UCBs6AxeDIx8Wszd1vyZPOwQ"),                  # youtube.com/@ppctvmedia
    ("CTV8 HD+", "UC907FcRL5pZOOB9wC4iBY9Q"),               # youtube.com/@CTV8HDPlus
    ("Huace Croton TV Cambodia", "UCGB9NdhFPeFhH9SxtcTOHXw"),  # youtube.com/@huacetvcambodia
    ("Prom Chau", "UC8tChlFiWfT5sJ0egXYvZew"),              # youtube.com/@promchau
    ("Sastra Film", "UCgRs-wjr54W4IjhRRQ99Arw"),            # youtube.com/@SastraFilmKH
    ("CTN TV", "UC7cyr5kbcN7jvG7No6lZ-wQ"),                 # youtube.com/@ctntvcambodia
]

PLAYLIST_TYPES = {"LOCKUP_CONTENT_TYPE_PLAYLIST", "LOCKUP_CONTENT_TYPE_PODCAST",
                  "LOCKUP_CONTENT_TYPE_ALBUM", "LOCKUP_CONTENT_TYPE_COURSE"}
VIDEO_TYPES = {"LOCKUP_CONTENT_TYPE_VIDEO"}
# A "next page" token only counts when it sits at the end of the item list itself
# (not in the page header, filter chips or "show unavailable videos" panels).
_ITEM_CONT = re.compile(r"(itemSectionRenderer|gridRenderer|richGridRenderer|appendContinuationItemsAction)"
                        r"/(contents|items|continuationItems)/\d+/continuationItem(Renderer|ViewModel)/")
_SKIP_PATH = re.compile(r"header|chip|engagementPanel|sheetViewModel")
_S = requests.Session()


# ── YouTube web API ──────────────────────────────
def _browse(**body):
    payload = {"context": {"client": {"clientName": "WEB", "clientVersion": CLIENT_VERSION,
                                      "hl": "en", "gl": "US"}}}
    payload.update(body)
    headers = {"User-Agent": UA, "Content-Type": "application/json",
               "Origin": "https://www.youtube.com", "Referer": "https://www.youtube.com/",
               "X-YouTube-Client-Name": "1", "X-YouTube-Client-Version": CLIENT_VERSION}
    r = _S.post(API_URL, data=json.dumps(payload), headers=headers, timeout=(5, 15))
    r.raise_for_status()
    return json.loads(r.text)


def _walk(node, key, path=""):
    """Yield (path, value) for every dict entry named `key`, depth first, in document order."""
    if isinstance(node, dict):
        for k, v in node.items():
            p = f"{path}/{k}"
            if k == key:
                yield p, v
            yield from _walk(v, key, p)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk(v, key, f"{path}/{i}")


def _root(data):
    """Continuation pages carry the items in onResponseReceivedActions; first pages in contents."""
    return data.get("onResponseReceivedActions") or data.get("contents") or {}


def parse_items(data):
    """-> list of dicts {id, type, title, thumb, badge} from the lockupViewModel cards."""
    out, seen = [], set()
    for path, lv in _walk(_root(data), "lockupViewModel"):
        if _SKIP_PATH.search(path) or not isinstance(lv, dict):
            continue
        cid = lv.get("contentId") or ""
        if not cid or cid in seen:
            continue
        seen.add(cid)
        title = (((lv.get("metadata") or {}).get("lockupMetadataViewModel") or {})
                 .get("title") or {}).get("content", "") or cid
        image = lv.get("contentImage") or {}
        sources = next((v for _, v in _walk(image, "sources") if v), [])
        thumb = (sources[-1].get("url", "") if sources else "").split("?")[0]
        badge = next((v.get("text", "") for _, v in _walk(image, "thumbnailBadgeViewModel")), "")
        out.append({"id": cid, "type": lv.get("contentType", ""), "title": title.strip(),
                    "thumb": thumb, "badge": badge})
    return out


def next_token(data):
    for path, cmd in _walk(_root(data), "continuationCommand"):
        if not isinstance(cmd, dict) or not cmd.get("token"):
            continue
        if _SKIP_PATH.search(path) or not _ITEM_CONT.search(path):
            continue
        return cmd["token"]
    return ""


def _duration(badge):
    parts = badge.split(":") if badge else []
    if not parts or not all(p.isdigit() for p in parts):
        return 0
    secs = 0
    for p in parts:
        secs = secs * 60 + int(p)
    return secs


# ── Kodi helpers ─────────────────────────────────
def _youtube_ready():
    """True if the YouTube add-on (needed for playback) is installed; otherwise ask Kodi to install it."""
    if xbmc.getCondVisibility(f"System.HasAddon({YOUTUBE_ADDON})"):
        return True
    kit.log("YouTube", "YouTube add-on missing; asking Kodi to install it", xbmc.LOGWARNING)
    xbmc.executebuiltin(f"InstallAddon({YOUTUBE_ADDON})", True)
    if xbmc.getCondVisibility(f"System.HasAddon({YOUTUBE_ADDON})"):
        return True
    xbmcgui.Dialog().ok("YouTube add-on needed",
                        "Please install the official YouTube add-on "
                        "(Add-ons > Install from repository > Kodi Add-on repository > "
                        "Video add-ons > YouTube), then open this menu again.")
    return False


def _add_video(item):
    li = xbmcgui.ListItem(label=item["title"])
    li.setArt({"thumb": item["thumb"], "icon": item["thumb"], "poster": item["thumb"],
               "fanart": item["thumb"]})
    tag = li.getVideoInfoTag()
    tag.setTitle(item["title"])
    secs = _duration(item["badge"])
    if secs:
        tag.setDuration(secs)
    li.setProperty("IsPlayable", "true")
    xbmcplugin.addDirectoryItem(handle=kit.PLUGIN_HANDLE, url=PLAY_URL.format(item["id"]),
                                listitem=li, isFolder=False)


def _load(url, first_page):
    """url is either an ID (first page) or 'cont:<token>' (next page)."""
    if url.startswith(CONT):
        return _browse(continuation=url[len(CONT):])
    return _browse(**first_page(url))


def _fail(what, err):
    kit.log("YouTube", f"{what} failed: {err}", xbmc.LOGERROR)
    xbmcgui.Dialog().notification("YouTube", "Could not load this list from YouTube. Try again later.",
                                  xbmcgui.NOTIFICATION_ERROR, 5000)
    xbmcplugin.endOfDirectory(kit.PLUGIN_HANDLE, succeeded=False)


# ── Menus ────────────────────────────────────────
def MENU():
    """All channels."""
    if not _youtube_ready():
        xbmcplugin.endOfDirectory(kit.PLUGIN_HANDLE, succeeded=False)
        return
    for name, cid in CHANNELS:
        kit.addDir(name, cid, "youtube_channel", "")
    xbmcplugin.endOfDirectory(kit.PLUGIN_HANDLE)


def CHANNEL(channel_id):
    if not _youtube_ready():
        xbmcplugin.endOfDirectory(kit.PLUGIN_HANDLE, succeeded=False)
        return
    kit.addDir("Playlists", channel_id, "yt_playlists", "")
    kit.addDir("Latest videos", channel_id, "yt_videos", "")
    xbmcplugin.endOfDirectory(kit.PLUGIN_HANDLE)


def PLAYLISTS(url):
    try:
        data = _load(url, lambda cid: {"browseId": cid, "params": TAB_PLAYLISTS})
    except Exception as e:
        return _fail("Playlists", e)
    count = 0
    for it in parse_items(data):
        if it["type"] not in PLAYLIST_TYPES or it["id"].startswith("RD"):
            continue
        label = f"{it['title']} [COLOR grey]({it['badge']})[/COLOR]" if it["badge"] else it["title"]
        kit.addDir(label, it["id"], "yt_playlist", it["thumb"])
        count += 1
    tok = next_token(data)
    if tok:
        kit.addDir("[B]Next Page >>>[/B]", CONT + tok, "yt_playlists", "")
    kit.log("YouTube", f"{count} playlists")
    xbmcplugin.setContent(kit.PLUGIN_HANDLE, "videos")
    xbmcplugin.endOfDirectory(kit.PLUGIN_HANDLE)


def _video_list(url, first_page, action, what):
    try:
        data = _load(url, first_page)
    except Exception as e:
        return _fail(what, e)
    count = 0
    for it in parse_items(data):
        if it["type"] in VIDEO_TYPES:
            _add_video(it)
            count += 1
    tok = next_token(data)
    if tok:
        kit.addDir("[B]Next Page >>>[/B]", CONT + tok, action, "")
    kit.log("YouTube", f"{count} videos ({what})")
    xbmcplugin.setContent(kit.PLUGIN_HANDLE, "episodes")
    xbmcplugin.endOfDirectory(kit.PLUGIN_HANDLE)


def PLAYLIST(url):
    _video_list(url, lambda pid: {"browseId": "VL" + pid}, "yt_playlist", "playlist")


def VIDEOS(url):
    _video_list(url, lambda cid: {"browseId": cid, "params": TAB_VIDEOS}, "yt_videos", "latest")
