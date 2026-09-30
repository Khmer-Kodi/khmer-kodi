# ────────────────────────────────────────────────
#  KHMERAVENUE.NET  (same page template as Video4Khmer, own catalogue)
#  Episodes are mostly Rumble (HLS up to 1080p), plus OK.ru / SOOP / TinyURL.
# ────────────────────────────────────────────────
import xbmcplugin
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
from resources.lib import sitekit as kit

TAG = "KhmerAvenue.net"
BASE = "https://www.khmeravenue.net/"
ICON = ""
CATEGORIES = [
    ("Latest", ""), ("Chinese Drama", "?video=Chinese-Drama&cat-id=28"),
    ("Korean Drama", "?video=Korean-Drama&cat-id=29"), ("Thai Drama", "?video=Thai-Drama&cat-id=18"),
    ("Khmer Drama", "?video=Khmer-Drama&cat-id=27"), ("Other Movies", "?video=Other-Movies&cat-id=30"),
]


def MENU():
    for label, query in CATEGORIES:
        kit.addDir(label, BASE + query, "index_khmeravenue_net", ICON)
    xbmcplugin.endOfDirectory(kit.PLUGIN_HANDLE)


def INDEX(url):
    _listing(url, include_pagination=True)


def SEARCH(query, end_directory=True):
    # Search pages show the site-wide pagination, so it is skipped here.
    _listing(f"{BASE}?search={quote_plus(query)}", label_suffix=" [COLOR violet]KhmerAvenue.net[/COLOR]",
             include_pagination=False, end_directory=end_directory)


def _listing(url, label_suffix="", include_pagination=True, end_directory=True):
    soup = BeautifulSoup(kit.fetch(url, BASE), "html.parser")
    count = 0
    for a in soup.select("a.box1[href]"):
        h2 = a.find("h2")
        img = a.find("img")
        title = (h2.get_text(" ", strip=True) if h2 else (img.get("alt") if img else "")) or "No Title"
        title = title.replace("​", "").strip()
        kit.addDir(f"{title}{label_suffix}", urljoin(BASE, a["href"]), "episode_khmeravenue_net",
                   kit.clean_image(img.get("src") if img else "", BASE))
        count += 1
    kit.log(TAG, f"{count} titles from {url}")

    if include_pagination:
        nxt = next((a for a in soup.select(".pagination a[href]")
                    if a.get_text(strip=True).lower() == "next"), None)
        if nxt:
            kit.addDir(kit.next_page_label(nxt["href"]), urljoin(BASE, nxt["href"]), "index_khmeravenue_net", "")
    if end_directory:
        xbmcplugin.endOfDirectory(kit.PLUGIN_HANDLE)


def EPISODES(url, icon=""):
    kit.show_episodes(TAG, url, icon, referer=BASE)
