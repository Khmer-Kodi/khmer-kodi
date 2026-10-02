#!/usr/bin/env bash
# Regression tests for plugin.video.KDubbed in a simulated Kodi (no network).
# Usage: bash tests/run_tests.sh          (from the repository root)
# Exit code 0 = all pass. Fixtures are real pages captured from each site.
set -u
cd "$(dirname "$0")/.."
D="$(pwd)/src/plugin.video.KDubbed"
export ENTRY=default.py
pip install -q requests beautifulsoup4 pyflakes --break-system-packages >/dev/null 2>&1 || true
find src -name __pycache__ -exec rm -rf {} + 2>/dev/null
python3 -m py_compile $(find "$D" -name '*.py') || { echo "COMPILE FAILED"; exit 1; }
LINT=$(python3 -m pyflakes $(find "$D" -name '*.py') | grep -v "imported but unused\|never used\|redefinition of unused")
find src -name __pycache__ -exec rm -rf {} + 2>/dev/null
[ -n "$LINT" ] && { echo "LINT FAILED:"; echo "$LINT"; exit 1; }
pass=0; fail=0
while IFS='|' read -r a u s; do
  [ -z "$a" ] && continue
  r=$(python3 tests/run.py "$D" "$a" "$u" "$s" 2>&1 | tail -1)
  if [[ $r == OK* ]] && [[ $r != *"ended=0 | items=0 [] | resolved=[]"* ]]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL $a [$s]: ${r:0:200}"; fi
done <<'CASES'
home||none
search||neterror
search||v4listing
search||kan_listing
khmer_livetv||neterror
khmer_livetv||urlmap
play_livetv|https://live.kh.malimarcdn.com/live/tvk2.stream/playlist.m3u8|none
play_livetv|https://live.kh.malimarcdn.com/live/tvk2.stream/playlist.m3u8|isa_on
play_livetv|http://live.happywatch99.com/livehd10/x.sdp/playlist.m3u8|none
index_vip|https://phumikhmer.vip/|neterror
index_sunday|https://www.sundaydrama.com/|neterror
index_idrama|https://www.idramahd.com/|neterror
index_phumik|https://www.phumikhmer1.club/|neterror
index_khmeravenue|https://www.khmeravenue.com/album/|neterror
index_merlkon|https://www.khmerdrama.com/album/|neterror
episode_craft4u|https://www.craft4u.top/myshow-01/|craft
episode_players|https://example.com/show/|playerlist
episode_players|https://example.com/show/|constvideos
play_direct|https://x.com/a.m3u8|none
menu_video4u||none
index_video4u|https://video4khmer.cam/?Category=Khmer-Drama&Menu=27&Khmer-Drama|v4listing
episode_video4khmer|https://video4khmer.cam/?Category=Movie&id=898|v4eps
episode_video4khmer|https://video4khmer.cam/?Category=Movie&id=5482|v4single
index_ckch7|x|none
menu_khmeravenue_net||none
index_khmeravenue_net|https://www.khmeravenue.net/|kan_listing
episode_khmeravenue_net|https://www.khmeravenue.net/?video=play&id=5180|kan_eps
index_khmeravenue_net|https://www.khmeravenue.net/|neterror
episode_khmeravenue_net|https://www.khmeravenue.net/?video=play&id=1|neterror
menu_thekomsan||none
index_thekomsan|https://www.thekomsan.com/feeds/posts/default?alt=json&max-results=24&start-index=1|urlmap
episode_thekomsan|https://www.thekomsan.com/x.html|tk_eps_rumble
episode_thekomsan|https://www.thekomsan.com/y.html|tk_eps_okru
index_thekomsan|https://www.thekomsan.com/feeds/posts/default?alt=json&max-results=24&start-index=1|neterror
menu_moviekhmer||none
index_moviekhmer|https://movie-khmer.com/chinese-drama/|mk_listing
episode_moviekhmer|https://movie-khmer.com/veasna-moyura/|mk_eps
index_moviekhmer|https://movie-khmer.com/|neterror
menu_khmerkomsan||none
index_khmerkomsan|https://www.khmerkomsan.net/category.php?cat=chinese-drama|kk_listing
episode_khmerkomsan|https://www.khmerkomsan.net/watch.php?vid=58d0b382a|kk_eps
index_khmerkomsan|https://www.khmerkomsan.net/|neterror
video_hosting|https://rumble.com/embed/v7d4mwk|urlmap
video_hosting|https://tinyurl.com/8883scjb|urlmap
menu_youtube|youtube|none
youtube_channel|UCAbHU5C61UNjwPV8MF5b2Bg|none
youtube_channel|UCd6StwIVjo8Zu4M4JAAFiSQ|none
youtube_channel|UCd6StwIVjo8Zu4M4JAAFiSQ|no_youtube
youtube_channel|UCm1syRy-B1uAkeecQS_2I3w|none
youtube_channel|UCHwYHdX37UUt6d9e1wAp9Bw|none
youtube_channel|UCp49cPgy5z2eTvE-kxtchrg|none
youtube_channel|UC8b-bkP65mcy4wMFEw3eirw|none
youtube_channel|UCBs6AxeDIx8Wszd1vyZPOwQ|none
youtube_channel|UC907FcRL5pZOOB9wC4iBY9Q|none
youtube_channel|UCGB9NdhFPeFhH9SxtcTOHXw|none
menu_youtube|youtube|no_youtube
CASES
echo "PASS=$pass FAIL=$fail"
[ "$fail" -eq 0 ]
