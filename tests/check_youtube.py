"""Detailed checks for the YouTube listings (fixtures follow the structure of real
youtubei/v1/browse responses captured on 2026-10-02). Prints PASS/FAIL lines."""
import os, sys, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
ADDON = os.path.join(os.path.dirname(HERE), "src", "plugin.video.KDubbed")
sys.path[:0] = [os.path.join(HERE, "stubs"), ADDON]
sys.argv = ["plugin://plugin.video.KDubbed/", "1", ""]
from resources.lib import youtube_channels as yt

FX = os.path.join(HERE, "fixtures")
load = lambda n: json.load(open(os.path.join(FX, n + ".json"), encoding="utf-8"))
results = []
def check(name, cond):
    results.append(bool(cond)); print(("PASS " if cond else "FAIL ") + name)

pl = load("yt_channel_playlists")
items = yt.parse_items(pl)
check("playlists parsed", [i["id"] for i in items][:2] == ["PLcrjVfrZRCdY", "PLV88nwwTQ8yk"])
check("playlist badge", items[0]["badge"] == "22 videos")
check("playlists next token (not header token)", yt.next_token(pl) == "PLAYLISTS_PAGE2_TOKEN")
check("last playlists page has no next", yt.next_token(load("yt_channel_playlists_next")) == "")
check("short playlist: side token ignored", yt.next_token(load("yt_playlist")) == "")
check("long playlist next token", yt.next_token(load("yt_playlist_long")) == "PLAYLIST_PAGE2_TOKEN")
check("playlist page 2 next token", yt.next_token(load("yt_playlist_next")) == "PLAYLIST_PAGE3_TOKEN")
check("videos next token (not chip token)", yt.next_token(load("yt_channel_videos")) == "VIDEOS_PAGE2_TOKEN")
v = yt.parse_items(load("yt_channel_videos"))
check("videos parsed", [i["id"] for i in v] == ["Qo-0uWH3gfE", "E4652Z6qUEA"])
check("duration parse", yt._duration("43:38") == 2618 and yt._duration("1:02:07") == 3727 and yt._duration("22 videos") == 0)
check("play url", yt.PLAY_URL.format("E4652Z6qUEA") == "plugin://plugin.video.youtube/play/?video_id=E4652Z6qUEA")

# End-to-end through default.py: request bodies and the items Kodi receives.
def run(action, url, scenario="yt"):
    env = dict(os.environ, ENTRY="default.py", DUMP="1")
    out = subprocess.run([sys.executable, os.path.join(HERE, "run.py"), ADDON, action, url, scenario],
                         capture_output=True, text=True, env=env).stdout
    get = lambda tag: json.loads(next(l[len(tag) + 1:] for l in out.splitlines() if l.startswith(tag + " ")))
    return get("ITEMS"), get("POSTS"), out.strip().splitlines()[-1]

it, posts, last = run("yt_playlist", "PLcrjVfrZRCdY")
check("playlist request uses VL id", posts and posts[0].get("browseId") == "VLPLcrjVfrZRCdY")
check("playlist items are playable YouTube links", it and all(u.startswith("plugin://plugin.video.youtube/play/?video_id=") and not f for _, u, f in it))
it, posts, last = run("yt_playlists", "UCAbHU5C61UNjwPV8MF5b2Bg")
check("playlists request uses channel + playlists tab", posts[0].get("browseId") == "UCAbHU5C61UNjwPV8MF5b2Bg" and posts[0].get("params") == yt.TAB_PLAYLISTS)
check("mix playlists skipped, folders + next page", len(it) == 3 and all(f for _, _, f in it) and "Next Page" in it[-1][0])
it, posts, last = run("yt_playlists", "cont:PLAYLISTS_PAGE2_TOKEN")
check("next page sends continuation", posts[0].get("continuation") == "PLAYLISTS_PAGE2_TOKEN" and "browseId" not in posts[0])
it, posts, last = run("yt_videos", "UCAbHU5C61UNjwPV8MF5b2Bg")
check("videos request uses videos tab", posts[0].get("params") == yt.TAB_VIDEOS and len(it) == 3)
it, posts, last = run("yt_playlists", "UCAbHU5C61UNjwPV8MF5b2Bg", "neterror")
check("network error -> notification, no crash", last.startswith("OK") and "Could not load" in last)
check("no API key prompt anywhere in add-on", "API key" not in open(yt.__file__).read().split("# ── YouTube web API")[1])


# Shift view (Estuary id 53) on every successful listing, with video content so Estuary offers it.
def view(action, url, scenario="yt", skin="skin.estuary"):
    env = dict(os.environ, ENTRY="default.py", DUMP="1", SKIN=skin)
    out = subprocess.run([sys.executable, os.path.join(HERE, "run.py"), ADDON, action, url, scenario],
                         capture_output=True, text=True, env=env).stdout
    return json.loads(next(l[5:] for l in out.splitlines() if l.startswith("VIEW ")))
for act, u, sc in (("home", "", "none"), ("yt_playlists", "UCAbHU5C61UNjwPV8MF5b2Bg", "yt"), ("index_khmerkomsan", "https://www.khmerkomsan.net/category.php?cat=on-air", "kk_listing")):
    v = view(act, u, sc)
    check(f"Shift view on {act}", "Container.SetViewMode(53)" in v["builtins"] and v["content"][-1:] == ["videos"])
check("no Shift id on other skins", "Container.SetViewMode(53)" not in view("home", "", "none", "skin.other")["builtins"])
check("no view change when a list fails", "Container.SetViewMode(53)" not in view("yt_playlists", "UCAbHU5C61UNjwPV8MF5b2Bg", "neterror")["builtins"])

# Khmer font: installed once into special://home/media/Fonts/arial.ttf and the Arial font set selected.
import tempfile, hashlib
FONT = os.path.join(ADDON, "resources", "fonts", "KhmerDubbedSans.ttf")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
def kodi(action, home, fontset="Default"):
    env = dict(os.environ, ENTRY="default.py", DUMP="1", KODI_HOME=home, FONTSET=fontset)
    out = subprocess.run([sys.executable, os.path.join(HERE, "run.py"), ADDON, action, "", "none"],
                         capture_output=True, text=True, env=env).stdout
    return json.loads(next(l[5:] for l in out.splitlines() if l.startswith("VIEW "))), out.strip().splitlines()[-1]
from fontTools.ttLib import TTFont
cm = TTFont(FONT).getBestCmap()
check("font has Khmer + Latin", all(c in cm for c in range(0x1780, 0x17DD)) and all(c in cm for c in range(0x20, 0x7F)))
home = tempfile.mkdtemp()
dest = os.path.join(home, "home", "media", "Fonts", "arial.ttf")
os.makedirs(os.path.dirname(dest)); open(dest, "wb").write(b"old user font")
v, last = kodi("home", home)
sets = [r for r in v["rpc"] if r["method"] == "Settings.SetSettingValue"]
check("home installs font as arial.ttf", os.path.exists(dest) and md5(dest) == md5(FONT) and last.startswith("OK"))
check("existing arial.ttf backed up", open(dest + ".bak", "rb").read() == b"old user font")
check("Arial font set selected", sets and sets[0]["params"] == {"setting": "lookandfeel.font", "value": "Arial"})
check("install notification", any("Khmer font installed" in str(d) for d in v["dialogs"]))
v, _ = kodi("home", home, fontset="Default")
check("second run changes nothing (user choice respected)", not [r for r in v["rpc"] if r["method"].startswith("Settings.")])
v, _ = kodi("khmer_font", home, fontset="Arial")
check("menu item re-run: already installed", any("already installed" in str(d) for d in v["dialogs"]))
v, _ = kodi("khmer_font", home, fontset="Default")
check("menu item re-selects Arial if user switched back", any(r["method"] == "Settings.SetSettingValue" for r in v["rpc"]))
home2 = tempfile.mkdtemp()
v, _ = kodi("home", home2, fontset="Arial")
check("Arial already selected -> ReloadSkin to load the new file", "ReloadSkin()" in v["builtins"])
print(f"YT_PASS={sum(results)} YT_FAIL={len(results) - sum(results)}")
sys.exit(0 if all(results) else 1)
