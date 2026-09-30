# ────────────────────────────────────────────────
#  SITEKIT: shared helpers for the site modules added in 1.8.16
#  (Movie-Khmer, Khmer Komsan, TheKomsan, KhmerAvenue.net)
# ────────────────────────────────────────────────
import re, sys, ast, json, xbmc, xbmcplugin, xbmcgui
from urllib.parse import quote_plus, urljoin
from html import unescape as html_unescape

from resources.lib.handlers_khmer import OpenURL as OpenURL_KH
from resources.lib.handlers_blogid import ADDON_ID

PLUGIN_HANDLE = int(sys.argv[1])


def log(tag, msg, level=xbmc.LOGINFO):
    xbmc.log(f"[{ADDON_ID}] [{tag}] {msg}", level)


def fetch(url, referer=None):
    headers = {"Referer": referer} if referer else None
    html = OpenURL_KH(url, headers=headers, as_text=True)
    if not html:
        raise Exception(f"Empty or failed response from URL: {url}")
    return html


def clean_image(src, base=""):
    """Absolute URL, strip '/../' segments, upgrade tiny Blogger thumbnails."""
    if not src:
        return ""
    src = urljoin(base, html_unescape(src.strip()))
    src = re.sub(r"^(https?://[^/]+)/(?:\.\./)+", r"\1/", src)
    src = re.sub(r"/s\d+(?:-[a-z]+)*(-c)?/", "/s400/", src)  # blogger s72-c -> s400
    return src


# ── Episode-list parsing ─────────────────────────
_LIST_PATTERNS = (
    r"options\.player_list\s*=\s*(\[[\s\S]*?\])\s*;",
    r"(?:const|var|let)\s+videos\s*=\s*(\[[\s\S]*?\])\s*;",
    r"(?:const|var|let)\s+list_vdoiframe\s*=\s*(\[[\s\S]*?\])\s*;",
)


def _script_bodies(html):
    # Skip JSON-LD blocks: some sites copy an escaped player_list into them.
    for m in re.finditer(r"<script\b([^>]*)>([\s\S]*?)</script>", html, re.I):
        if "ld+json" in m.group(1).lower():
            continue
        yield m.group(2)


def _load_array(raw):
    raw = raw.strip()
    try:
        return json.loads(raw)
    except Exception:
        pass
    try:
        return ast.literal_eval(raw.replace("null", "None").replace("true", "True").replace("false", "False"))
    except Exception:
        pass
    try:  # JS object literal: unquoted keys, single quotes, trailing commas
        js = re.sub(r"([{,]\s*)([A-Za-z_]\w*)\s*:", r'\1"\2":', raw)
        js = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", lambda m: json.dumps(m.group(1)), js)
        js = re.sub(r",\s*([\]}])", r"\1", js)
        return json.loads(js)
    except Exception:
        pass
    items = []
    for obj in re.findall(r"\{[^{}]*\}", raw):
        f = re.search(r"['\"]?file['\"]?\s*:\s*['\"]([^'\"]+)['\"]", obj)
        t = re.search(r"['\"]?title['\"]?\s*:\s*['\"]([^'\"]*)['\"]", obj)
        if f:
            items.append({"file": f.group(1), "title": t.group(1) if t else ""})
    return items


def parse_video_list(html):
    for body in _script_bodies(html):
        for pat in _LIST_PATTERNS:
            m = re.search(pat, body)
            if not m:
                continue
            items = _load_array(m.group(1)) or []
            out = []
            for it in items:
                if isinstance(it, dict):
                    f = (it.get("file") or it.get("src") or it.get("url") or "").strip()
                    if f:
                        out.append({"file": html_unescape(f).replace("\\/", "/"),
                                    "title": html_unescape(str(it.get("title") or "")).strip()})
            if out:
                return out
    return []


# ── Link routing ─────────────────────────────────
def route_for(vurl, referer=""):
    """Return (url, action) for one episode link."""
    vurl = vurl.strip()
    if vurl.startswith("//"):
        vurl = "https:" + vurl
    low = vurl.lower()
    if "ok.ru/" in low:
        return vurl.split("?")[0], "video_hosting"
    if "rumble.com/embed/" in low or "tinyurl.com/" in low or "facebook.com/" in low:
        return vurl, "video_hosting"          # resolved in handlers_playback.VIDEO_HOSTING
    if re.search(r"\.(mp4|m3u8)(\?|/|$)", low):
        return (f"{vurl}|Referer={referer}" if referer else vurl), "play_direct"
    return vurl, "video_hosting"


def episode_label(title, index, total):
    if total == 1:
        return title or "Play"
    m = re.search(r"(?:\bEp(?:isode)?|\bPart)\.?\s*(\d+)|^(\d{1,3})[.\s]|,\s*(\d{1,3})\s*$", title or "", re.I)
    num = next((g for g in (m.groups() if m else ()) if g), None)
    return f"Episode {int(num):02d}" if num else f"Episode {index:02d}"


def list_episodes(items, icon="", referer=""):
    seen, used = set(), {}
    for i, it in enumerate(items, 1):
        url, action = route_for(it["file"], referer)
        if url in seen:
            continue
        seen.add(url)
        label = episode_label(it.get("title", ""), i, len(items))
        used[label] = used.get(label, 0) + 1
        if used[label] > 1:
            label += f" (alt {used[label] - 1})"
        addLink(label, url, action, icon)


def show_episodes(tag, url, icon="", referer=""):
    try:
        html = fetch(url, referer)
    except Exception as e:
        log(tag, f"Episode page failed: {e}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok(tag, "Failed to load this title. The site may be down.")
        xbmcplugin.endOfDirectory(PLUGIN_HANDLE)
        return
    items = parse_video_list(html)
    if not items:
        xbmcgui.Dialog().ok("No Episodes Found", "No playable episodes were found on this page.")
    else:
        list_episodes(items, icon, referer)
    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)


def next_page_label(href):
    m = re.search(r"(?:[?&]page=|/page/)(\d+)", href or "")
    return f"[B]Next Page ({m.group(1)}) >>>[/B]" if m else "[B]Next Page >>>[/B]"


# ── Directory helpers ────────────────────────────
def _art(li, icon):
    li.setArt({"thumb": icon, "icon": icon, "poster": icon,
               "landscape": icon, "fanart": icon, "banner": icon})


def _plugin_url(name, url, action, icon):
    return (f"{sys.argv[0]}?url={quote_plus(str(url))}&action={quote_plus(str(action))}"
            f"&name={quote_plus(str(name))}&icon={quote_plus(str(icon))}")


def addDir(name, url, action, icon=""):
    li = xbmcgui.ListItem(label=name)
    _art(li, icon)
    li.getVideoInfoTag().setTitle(name)
    xbmcplugin.addDirectoryItem(handle=PLUGIN_HANDLE, url=_plugin_url(name, url, action, icon),
                                listitem=li, isFolder=True)


def addLink(name, url, action, icon=""):
    li = xbmcgui.ListItem(label=name)
    _art(li, icon)
    li.setProperty("IsPlayable", "true")
    li.getVideoInfoTag().setTitle(name)
    xbmcplugin.addDirectoryItem(handle=PLUGIN_HANDLE, url=_plugin_url(name, url, action, icon),
                                listitem=li, isFolder=False)
