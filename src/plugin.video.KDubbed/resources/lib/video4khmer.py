# ────────────────────────────────────────────────
#  VIDEO4KHMER SITE HANDLER  (video4khmer.cam layout, 2026)
#  The old video4khmer36.com domain is parked; the site moved to
#  video4khmer.cam with a new page layout.
# ────────────────────────────────────────────────
import re, sys, ast, xbmc, xbmcplugin, xbmcgui
from urllib.parse import quote_plus, urljoin
from html import unescape as html_unescape
from bs4 import BeautifulSoup

# ── Local Handlers ──────────────────────────────
from resources.lib.handlers_khmer import OpenURL as OpenURL_KH
from resources.lib.handlers_blogid import ADDON_ID

# ── Site constants ──────────────────────────────
VIDEO4KHMER = "https://video4khmer.cam/"
ICON_VIDEO4U = VIDEO4KHMER + "home/img/logo.png"
HEADERS = {"Referer": VIDEO4KHMER}
PLUGIN_HANDLE = int(sys.argv[1])

CATEGORIES = [
    ("Latest",         VIDEO4KHMER),
    ("Khmer Drama",    VIDEO4KHMER + "?Category=Khmer-Drama&Menu=27&Khmer-Drama"),
    ("Chinese Drama",  VIDEO4KHMER + "?Category=Chinese-Drama&Menu=28&Chinese-Drama"),
    ("Thai Drama",     VIDEO4KHMER + "?Category=Thai-Drama&Menu=18&Thai-Drama"),
    ("Korean Drama",   VIDEO4KHMER + "?Category=Korean-Drama&Menu=29&Korean-Drama"),
    ("Other Drama",    VIDEO4KHMER + "?Category=Other-Drama&Menu=30&Other-Drama"),
]


def _log(msg, level=xbmc.LOGINFO):
    xbmc.log(f"[{ADDON_ID}] [video4khmer] {msg}", level)


def _fetch(url):
    html = OpenURL_KH(url, headers=HEADERS, as_text=True)
    if not html:
        raise Exception(f"Empty or failed response from URL: {url}")
    return html


def _clean_image(src):
    # Site uses paths like https://phumikhmer2.com/../admin/img/x.jpg
    if not src:
        return ""
    src = urljoin(VIDEO4KHMER, src.strip())
    return re.sub(r"^(https?://[^/]+)/(?:\.\./)+", r"\1/", src)


############## MENU ##############
def MENU_VIDEO4U():
    for label, url in CATEGORIES:
        addDir(label, url, "index_video4u", ICON_VIDEO4U)
    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)


############## LISTINGS ##############
def INDEX_VIDEO4U(url):
    _render_listing(url, include_pagination=True)


def SEARCH_VIDEO4U(search_term, end_directory=True):
    url = f"{VIDEO4KHMER}?search={quote_plus(search_term)}"
    # Search pages show the site-wide pagination, so it is skipped here.
    _render_listing(url, label_suffix=" [COLOR orange]Video4Khmer[/COLOR]",
                    include_pagination=False, end_directory=end_directory)


def _render_listing(url, label_suffix="", include_pagination=True, end_directory=True):
    soup = BeautifulSoup(_fetch(url), "html.parser")

    count = 0
    for a in soup.select("a.box1[href]"):
        title = (a.get("aria-label") or "").strip()
        if not title:
            h2 = a.find("h2")
            title = h2.get_text(strip=True) if h2 else "No Title"
        img = a.find("img")
        image = _clean_image(img.get("src") if img else "")
        link = urljoin(VIDEO4KHMER, a["href"])
        addDir(f"{html_unescape(title)}{label_suffix}", link, "episode_video4khmer", image)
        count += 1
    _log(f"{count} titles from {url}")

    if include_pagination:
        nxt = next((a for a in soup.select(".pagination a[href]")
                    if a.get_text(strip=True).lower() == "next"), None)
        if nxt:
            page = re.search(r"[?&]page=(\d+)", nxt["href"])
            label = f"[B]Next Page ({page.group(1)}) >>>[/B]" if page else "[B]Next Page >>>[/B]"
            addDir(label, urljoin(VIDEO4KHMER, nxt["href"]), "index_video4u", "")

    if end_directory:
        xbmcplugin.endOfDirectory(PLUGIN_HANDLE)


############## EPISODES ##############
def _parse_player_list(html):
    m = re.search(r"options\.player_list\s*=\s*(\[[\s\S]*?\])\s*;", html)
    if not m:
        return []
    raw = m.group(1)
    try:
        items = ast.literal_eval(raw.replace("null", "None"))
        return [it for it in items if isinstance(it, dict) and it.get("file")]
    except Exception as e:
        _log(f"literal_eval failed, using regex: {e}", xbmc.LOGWARNING)
        return [{"file": f, "title": t} for f, t in re.findall(
            r"['\"]file['\"]\s*:\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]title['\"]\s*:\s*['\"]([^'\"]*)['\"]", raw)]


def EPISODE_VIDEO4KHMER(url, icon=""):
    try:
        html = _fetch(url)
    except Exception as e:
        _log(f"Episode page failed: {e}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok("Video4Khmer", "Failed to load this title. The site may be down.")
        xbmcplugin.endOfDirectory(PLUGIN_HANDLE)
        return

    items = _parse_player_list(html)
    if not items:
        xbmcgui.Dialog().ok("No Episodes Found", "No playable episodes were found on this page.")
        xbmcplugin.endOfDirectory(PLUGIN_HANDLE)
        return

    for i, it in enumerate(items, 1):
        vurl = html_unescape(it["file"].strip())
        title = html_unescape((it.get("title") or "").strip())
        ep = re.search(r"\b(?:Ep(?:isode)?|Part)\.?\s*(\d+)", title, re.I)
        if len(items) == 1:
            label = title or "Play"
        else:
            label = f"Episode {int(ep.group(1)):02d}" if ep else f"Episode {i:02d}"

        if "ok.ru/" in vurl:
            vurl = vurl.split("?")[0]
            mode = "video_hosting"
        elif "ug.link/" in vurl:
            # Files on the uploader's UGREEN NAS; only reachable while that device is online.
            vurl = f"{vurl}|Referer={VIDEO4KHMER}"  # Play_VIDEO adds the User-Agent
            mode = "play_direct"
        elif re.search(r"\.(mp4|m3u8)(\?|$)", vurl):
            mode = "play_direct"
        else:
            mode = "video_hosting"
        addLink(label, vurl, mode, icon)

    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)


# ────────────────────────────────────────────────
#  BASIC DIRECTORY HELPERS
# ────────────────────────────────────────────────
def _art(li, iconimage):
    li.setArt({"thumb": iconimage, "icon": iconimage, "poster": iconimage,
               "landscape": iconimage, "fanart": iconimage, "banner": iconimage})


def _plugin_url(name, url, action, iconimage):
    return (f"{sys.argv[0]}?url={quote_plus(str(url))}&action={quote_plus(str(action))}"
            f"&name={quote_plus(str(name))}&icon={quote_plus(str(iconimage))}")


def addDir(name, url, action, iconimage=""):
    li = xbmcgui.ListItem(label=name)
    _art(li, iconimage)
    li.getVideoInfoTag().setTitle(name)
    xbmcplugin.addDirectoryItem(handle=PLUGIN_HANDLE, url=_plugin_url(name, url, action, iconimage),
                                listitem=li, isFolder=True)


def addLink(name, url, action, iconimage=""):
    li = xbmcgui.ListItem(label=name)
    _art(li, iconimage)
    li.setProperty("IsPlayable", "true")
    li.getVideoInfoTag().setTitle(name)
    xbmcplugin.addDirectoryItem(handle=PLUGIN_HANDLE, url=_plugin_url(name, url, action, iconimage),
                                listitem=li, isFolder=False)
