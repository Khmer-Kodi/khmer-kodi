# ────────────────────────────────────────────────
#  KHMER LIVE TV
#  Channel list: livetv.json in the GitHub repository (kept up to date by the
#  weekly check), with a copy bundled in the add-on as a fallback.
# ────────────────────────────────────────────────
import os, sys, json, xbmc, xbmcaddon, xbmcgui, xbmcplugin
from urllib.parse import quote_plus, urlparse
from resources.lib import sitekit as kit
from resources.lib.handlers_khmer import OpenURL as OpenURL_KH

LIST_URL = "https://raw.githubusercontent.com/Khmer-kodi/khmer-kodi/main/livetv.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0 Safari/537.36"

# Some broadcasters only answer when the request looks like it came from their own player.
REFERERS = {
    "metfone.com.kh": "https://live-ali7.tv360.metfone.com.kh/",
}


def _addon_path():
    return xbmcaddon.Addon().getAddonInfo("path")


def load_channels():
    """Online list first; bundled copy if GitHub can't be reached."""
    try:
        txt = OpenURL_KH(LIST_URL, as_text=True)
        data = json.loads(txt)
        if data.get("channels"):
            return data["channels"], "online"
    except Exception as e:
        kit.log("LiveTV", f"Online channel list unavailable ({e}); using bundled list", xbmc.LOGWARNING)
    with open(os.path.join(_addon_path(), "resources", "livetv.json"), encoding="utf-8") as f:
        return json.load(f).get("channels", []), "bundled"


def MENU():
    try:
        channels, source = load_channels()
    except Exception as e:
        kit.log("LiveTV", f"No channel list: {e}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok("Khmer Live TV", "The channel list could not be loaded.")
        xbmcplugin.endOfDirectory(kit.PLUGIN_HANDLE, succeeded=False)
        return
    kit.log("LiveTV", f"{len(channels)} channels ({source} list)")
    icon = os.path.join(_addon_path(), "resources", "images", "khmertv.png")
    for ch in channels:
        name, url = ch.get("name", "").strip(), ch.get("url", "").strip()
        if not name or not url:
            continue
        logo = ch.get("logo") or icon
        li = xbmcgui.ListItem(label=name)
        li.setArt({"thumb": logo, "icon": logo, "poster": logo})
        li.getVideoInfoTag().setTitle(name)
        li.setProperty("IsPlayable", "true")
        u = f"{sys.argv[0]}?action=play_livetv&url={quote_plus(url)}&name={quote_plus(name)}"
        xbmcplugin.addDirectoryItem(kit.PLUGIN_HANDLE, u, li, False)
    xbmcplugin.endOfDirectory(kit.PLUGIN_HANDLE)


def _headers_for(url):
    host = urlparse(url).netloc.lower()
    headers = {"User-Agent": UA}
    for domain, ref in REFERERS.items():
        if host.endswith(domain):
            headers["Referer"] = ref
    return "&".join(f"{k}={quote_plus(v)}" for k, v in headers.items())


def PLAY(url, name=""):
    """Play an HLS live stream. Uses InputStream Adaptive only if it is installed AND enabled;
    otherwise Kodi's built-in player handles the HLS stream directly."""
    item = xbmcgui.ListItem(path=f"{url}|{_headers_for(url)}")
    if name:
        item.getVideoInfoTag().setTitle(name)
    item.setMimeType("application/vnd.apple.mpegurl")
    item.setContentLookup(False)
    if xbmc.getCondVisibility("System.AddonIsEnabled(inputstream.adaptive)"):
        item.setProperty("inputstream", "inputstream.adaptive")
    kit.log("LiveTV", f"Playing {name or url}")
    xbmcplugin.setResolvedUrl(kit.PLUGIN_HANDLE, True, item)
