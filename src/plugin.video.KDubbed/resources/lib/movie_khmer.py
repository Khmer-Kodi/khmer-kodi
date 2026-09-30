# ────────────────────────────────────────────────
#  MOVIE-KHMER.COM  (WordPress "Publisher" theme; OK.ru episodes)
# ────────────────────────────────────────────────
import xbmcplugin
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
from resources.lib import sitekit as kit

TAG = "Movie-Khmer"
BASE = "https://movie-khmer.com/"
ICON = ""
CATEGORIES = [
    ("Chinese Drama", "chinese-drama/"), ("Korean Drama", "korean-drama/"),
    ("Khmer Drama", "khmer-drama/"), ("Thai Drama", "thai-drama/"),
    ("India Drama", "india-drama/"), ("Chinese Movie", "chinese-movie/"),
    ("Korean Movie", "korean-movie/"), ("Khmer Movie", "khmer-movie/"),
    ("Thai Movie", "thai-movie/"),
]


def MENU():
    kit.addDir("Latest", BASE, "index_moviekhmer", ICON)
    for label, path in CATEGORIES:
        kit.addDir(label, BASE + path, "index_moviekhmer", ICON)
    xbmcplugin.endOfDirectory(kit.PLUGIN_HANDLE)


def INDEX(url):
    _listing(url, include_pagination=True)


def SEARCH(query, end_directory=True):
    _listing(f"{BASE}?s={quote_plus(query)}", label_suffix=" [COLOR lime]Movie-Khmer[/COLOR]",
             include_pagination=False, end_directory=end_directory)


def _listing(url, label_suffix="", include_pagination=True, end_directory=True):
    soup = BeautifulSoup(kit.fetch(url, BASE), "html.parser")
    count = 0
    for art in soup.select("article"):
        a = art.select_one("h2.title a[href], h3.title a[href], .title a[href]")
        if not a:
            continue
        title = (a.get("title") or a.get_text(" ", strip=True)).strip()
        feat = art.select_one(".featured a")
        img = feat.get("data-src") if feat else ""
        if not img:
            tag = art.find("img")
            img = (tag.get("data-src") or tag.get("src")) if tag else ""
        kit.addDir(f"{title}{label_suffix}", urljoin(BASE, a["href"]), "episode_moviekhmer",
                   kit.clean_image(img, BASE))
        count += 1
    kit.log(TAG, f"{count} titles from {url}")

    if include_pagination:
        nxt = soup.select_one("a.next.page-numbers[href]")
        if nxt:
            kit.addDir(kit.next_page_label(nxt["href"]), urljoin(BASE, nxt["href"]), "index_moviekhmer", "")
    if end_directory:
        xbmcplugin.endOfDirectory(kit.PLUGIN_HANDLE)


def EPISODES(url, icon=""):
    kit.show_episodes(TAG, url, icon, referer=BASE)
