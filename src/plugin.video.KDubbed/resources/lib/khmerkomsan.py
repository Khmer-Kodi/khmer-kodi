# ────────────────────────────────────────────────
#  KHMERKOMSAN.NET  (PHP Melody: category.php / watch.php; OK.ru episodes)
# ────────────────────────────────────────────────
import xbmcplugin
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
from resources.lib import sitekit as kit

TAG = "Khmer Komsan"
BASE = "https://www.khmerkomsan.net/"
ICON = ""
CATEGORIES = [
    ("On Air", "on-air"), ("Chinese Drama", "chinese-drama"), ("Korean Drama", "korean-drama"),
    ("Khmer Drama", "khmer-drama"), ("Thai Drama", "thai-drama"), ("Thai Boran", "thai-boran"),
    ("Chinese Movie", "chinese-movie"), ("Korean Movie", "korean-movie"),
    ("Khmer Movie", "khmer-movie"), ("Thai Movie", "thai-movie"),
]


def MENU():
    for label, cat in CATEGORIES:
        kit.addDir(label, f"{BASE}category.php?cat={cat}", "index_khmerkomsan", ICON)
    xbmcplugin.endOfDirectory(kit.PLUGIN_HANDLE)


def INDEX(url):
    _listing(url, include_pagination=True)


def SEARCH(query, end_directory=True):
    _listing(f"{BASE}search.php?keywords={quote_plus(query)}",
             label_suffix=" [COLOR yellow]Khmer Komsan[/COLOR]",
             include_pagination=False, end_directory=end_directory)


def _listing(url, label_suffix="", include_pagination=True, end_directory=True):
    soup = BeautifulSoup(kit.fetch(url, BASE), "html.parser")
    count = 0
    for card in soup.select("div.card.shadow-sm"):
        a = card.select_one("h3.post-title a[href]") or card.select_one("a[href*='watch.php']")
        if not a:
            continue
        img = card.find("img")
        title = (a.get("title") or a.get_text(strip=True) or (img.get("title") if img else "") or "No Title")
        title = title.replace("​", "").strip()
        image = (img.get("data-echo") or img.get("data-src") or img.get("src")) if img else ""
        kit.addDir(f"{title}{label_suffix}", urljoin(BASE, a["href"]), "episode_khmerkomsan",
                   kit.clean_image(image, BASE))
        count += 1
    kit.log(TAG, f"{count} titles from {url}")

    if include_pagination:
        nxt = next((a for a in soup.select("ul.pagination a[href]")
                    if a.get_text(strip=True) == "»" and a["href"] != "#"), None)
        if nxt:
            kit.addDir(kit.next_page_label(nxt["href"]), urljoin(BASE, nxt["href"]), "index_khmerkomsan", "")
    if end_directory:
        xbmcplugin.endOfDirectory(kit.PLUGIN_HANDLE)


def EPISODES(url, icon=""):
    kit.show_episodes(TAG, url, icon, referer=BASE)
