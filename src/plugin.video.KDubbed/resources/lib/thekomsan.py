# ────────────────────────────────────────────────
#  THEKOMSAN.COM  (Blogger; listings via the JSON feed)
#  Episodes are OK.ru or direct 720p MP4 files on Rumble's CDN.
#  This is where the old Ckh7 site moved to.
# ────────────────────────────────────────────────
import json, xbmcplugin
from urllib.parse import quote, quote_plus
from resources.lib import sitekit as kit

TAG = "TheKomsan"
BASE = "https://www.thekomsan.com/"
ICON = ""
PAGE_SIZE = 24
LABELS = [("Latest", ""), ("On Air", "On Air"), ("Chinese Drama", "Chinese Drama"),
          ("Korean Drama", "Korean Drama"), ("Chinese Movie", "Chinese Movie")]


def _feed_url(label="", start=1, query=""):
    path = f"feeds/posts/default/-/{quote(label)}" if label else "feeds/posts/default"
    url = f"{BASE}{path}?alt=json&max-results={PAGE_SIZE}&start-index={start}"
    return url + (f"&q={quote_plus(query)}" if query else "")


def MENU():
    for name, label in LABELS:
        kit.addDir(name, _feed_url(label), "index_thekomsan", ICON)
    xbmcplugin.endOfDirectory(kit.PLUGIN_HANDLE)


def INDEX(url):
    _listing(url, include_pagination=True)


def SEARCH(query, end_directory=True):
    _listing(_feed_url(query=query), label_suffix=" [COLOR skyblue]TheKomsan[/COLOR]",
             include_pagination=False, end_directory=end_directory)


def _listing(url, label_suffix="", include_pagination=True, end_directory=True):
    feed = json.loads(kit.fetch(url, BASE)).get("feed", {})
    entries = feed.get("entry", []) or []
    for e in entries:
        title = e.get("title", {}).get("$t", "No Title").strip()
        link = next((l.get("href") for l in e.get("link", []) if l.get("rel") == "alternate"), "")
        thumb = (e.get("media$thumbnail") or {}).get("url", "")
        if link:
            kit.addDir(f"{title}{label_suffix}", link, "episode_thekomsan", kit.clean_image(thumb))
    kit.log(TAG, f"{len(entries)} titles from {url}")

    if include_pagination and entries:
        total = int(feed.get("openSearch$totalResults", {}).get("$t", 0) or 0)
        start = int(feed.get("openSearch$startIndex", {}).get("$t", 1) or 1)
        nxt = start + len(entries)
        if nxt <= total:
            page = (start - 1) // PAGE_SIZE + 2
            next_url = url.replace(f"start-index={start}", f"start-index={nxt}")
            kit.addDir(f"[B]Next Page ({page}) >>>[/B]", next_url, "index_thekomsan", "")
    if end_directory:
        xbmcplugin.endOfDirectory(kit.PLUGIN_HANDLE)


def EPISODES(url, icon=""):
    kit.show_episodes(TAG, url, icon, referer=BASE)
