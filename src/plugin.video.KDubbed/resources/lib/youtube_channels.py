# ────────────────────────────────────────────────
#  YOUTUBE CHANNELS (played through Kodi's official YouTube add-on)
#  To add a channel: append (name, channel_id) to CHANNELS. The main menu is built
#  from this list automatically.
# ────────────────────────────────────────────────
import xbmc, xbmcgui, xbmcplugin
from resources.lib import sitekit as kit

YOUTUBE_ADDON = "plugin.video.youtube"
YT = f"plugin://{YOUTUBE_ADDON}"

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
]


def _youtube_ready():
    """True if the YouTube add-on is installed; otherwise ask Kodi to install it."""
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


def _folder(label, plugin_url, icon=""):
    li = xbmcgui.ListItem(label=label)
    li.setArt({"thumb": icon, "icon": icon})
    xbmcplugin.addDirectoryItem(handle=kit.PLUGIN_HANDLE, url=plugin_url, listitem=li, isFolder=True)


def MENU():
    """Top-level YouTube menu: one entry per channel (or straight into it if only one)."""
    if not _youtube_ready():
        xbmcplugin.endOfDirectory(kit.PLUGIN_HANDLE, succeeded=False)
        return
    if len(CHANNELS) == 1:
        return CHANNEL(CHANNELS[0][1])
    for name, cid in CHANNELS:
        kit.addDir(name, cid, "youtube_channel", "")
    xbmcplugin.endOfDirectory(kit.PLUGIN_HANDLE)


def CHANNEL(channel_id):
    if not _youtube_ready():
        xbmcplugin.endOfDirectory(kit.PLUGIN_HANDLE, succeeded=False)
        return
    _folder("Playlists", f"{YT}/channel/{channel_id}/playlists/")
    _folder("Latest videos", f"{YT}/channel/{channel_id}/")
    xbmcplugin.endOfDirectory(kit.PLUGIN_HANDLE)
