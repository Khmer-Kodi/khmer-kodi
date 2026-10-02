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

print(f"YT_PASS={sum(results)} YT_FAIL={len(results) - sum(results)}")
sys.exit(0 if all(results) else 1)
