# ────────────────────────────────────────────────
#  KHMER FONT
#  Kodi's default skin font has no Khmer letters, so Khmer titles show as boxes.
#  Fix: put a font with Latin + Khmer (Noto Sans + Noto Sans Khmer, SIL OFL,
#  merged into resources/fonts/KhmerDubbedSans.ttf) at special://home/media/Fonts/arial.ttf
#  and switch the skin to its "Arial based" font set. Kodi looks for arial.ttf in
#  special://home/media/Fonts before its own copy, so this only affects this Kodi
#  profile, survives Kodi updates, and is undone by choosing the "Default" fonts again
#  (Settings > Interface > Skin > Fonts). Any arial.ttf already there is kept as arial.ttf.bak.
# ────────────────────────────────────────────────
import os, json, hashlib, xbmc, xbmcaddon, xbmcgui, xbmcvfs

FONT_FILE = "KhmerDubbedSans.ttf"
FONT_DIR = "special://home/media/Fonts/"
TARGET_NAME = "arial.ttf"
FONTSET = "Arial"
SETTING = "lookandfeel.font"
TAG = "[plugin.video.KDubbed] Khmer font:"


def _md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _rpc(method, **params):
    req = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    try:
        return json.loads(xbmc.executeJSONRPC(json.dumps(req)) or "{}")
    except Exception as e:
        xbmc.log(f"{TAG} JSON-RPC {method} failed: {e}", xbmc.LOGWARNING)
        return {}


def _paths():
    src = os.path.join(xbmcaddon.Addon().getAddonInfo("path"), "resources", "fonts", FONT_FILE)
    dest_dir = xbmcvfs.translatePath(FONT_DIR)
    profile = xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo("profile"))
    return src, dest_dir, os.path.join(dest_dir, TARGET_NAME), os.path.join(profile, "khmer_font.done")


def ensure(force=False):
    """Install the Khmer font and select the Arial font set. Runs automatically once per
    font version (from the home menu); force=True when the user picks it from the menu.
    Returns True if anything changed."""
    try:
        src, dest_dir, dest, marker = _paths()
        if not os.path.exists(src):
            return False
        want = _md5(src)
        done = open(marker).read().strip() if os.path.exists(marker) else ""
        if done == want and not force:
            return False          # already done for this font version; respect later user choices

        changed = False
        if not (os.path.exists(dest) and _md5(dest) == want):
            os.makedirs(dest_dir, exist_ok=True)
            backup = dest + ".bak"
            if os.path.exists(dest) and not os.path.exists(backup):
                os.replace(dest, backup)
            with open(src, "rb") as fi, open(dest + ".tmp", "wb") as fo:
                fo.write(fi.read())
            os.replace(dest + ".tmp", dest)
            changed = True
            xbmc.log(f"{TAG} installed {dest}", xbmc.LOGINFO)

        current = (_rpc("Settings.GetSettingValue", setting=SETTING).get("result") or {}).get("value")
        if current != FONTSET:
            res = _rpc("Settings.SetSettingValue", setting=SETTING, value=FONTSET)
            if res.get("result") is True:
                changed = True           # Kodi reloads the skin fonts itself
                xbmc.log(f"{TAG} font set changed from {current!r} to {FONTSET}", xbmc.LOGINFO)
            else:
                xbmc.log(f"{TAG} this skin has no '{FONTSET}' font set ({res})", xbmc.LOGWARNING)
        elif changed:
            xbmc.executebuiltin("ReloadSkin()")   # font set already Arial: reload to pick up the new file

        os.makedirs(os.path.dirname(marker), exist_ok=True)
        with open(marker, "w") as f:
            f.write(want)
        if changed:
            xbmcgui.Dialog().notification("Khmer Dubbed", "Khmer font installed", xbmcgui.NOTIFICATION_INFO, 4000)
        elif force:
            xbmcgui.Dialog().notification("Khmer Dubbed", "Khmer font is already installed", xbmcgui.NOTIFICATION_INFO, 3000)
        return changed
    except Exception as e:
        xbmc.log(f"{TAG} failed: {e}", xbmc.LOGWARNING)
        if force:
            xbmcgui.Dialog().ok("Khmer font", f"The Khmer font could not be installed:\n{e}")
        return False
