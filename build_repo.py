#!/usr/bin/env python3
"""Build the Kodi repository from ./src.

Usage: python3 build_repo.py <github-owner> <github-repo> [branch]
Writes: zips/<id>/<id>-<version>.zip, addons.xml, addons.xml.md5, and the
repository add-on in src/<repo-id>. Re-run after every change, then commit + push.
"""
import hashlib, os, re, shutil, sys, zipfile
import xml.etree.ElementTree as ET

owner, repo = sys.argv[1], sys.argv[2]
branch = sys.argv[3] if len(sys.argv) > 3 else "main"
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC, ZIPS = os.path.join(ROOT, "src"), os.path.join(ROOT, "zips")
RAW = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/"
REPO_ID = "repository.khmerkodi.personal"
REPO_VERSION = "1.0.0"

# 1. repository add-on (points Kodi at this GitHub repo + Gujal00 for ResolveURL)
rdir = os.path.join(SRC, REPO_ID)
os.makedirs(rdir, exist_ok=True)
with open(os.path.join(rdir, "addon.xml"), "w", encoding="utf-8") as f:
    f.write(f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<addon id="{REPO_ID}" name="Khmer Kodi (personal) Repository" version="{REPO_VERSION}" provider-name="{owner}">
  <extension point="xbmc.addon.repository" name="Khmer Kodi (personal) Repository">
    <dir>
      <info compressed="false">{RAW}addons.xml</info>
      <checksum>{RAW}addons.xml.md5</checksum>
      <datadir zip="true">{RAW}zips/</datadir>
    </dir>
    <dir>
      <info compressed="false">https://raw.githubusercontent.com/Gujal00/smrzips/master/addons.xml</info>
      <checksum>https://raw.githubusercontent.com/Gujal00/smrzips/master/addons.xml.md5</checksum>
      <datadir zip="true">https://raw.githubusercontent.com/Gujal00/smrzips/master/zips/</datadir>
    </dir>
  </extension>
  <extension point="xbmc.addon.metadata">
    <summary>Fixed Khmer Dubbed add-on with automatic updates</summary>
    <description>Personal repository for the maintained Khmer Dubbed add-on. Also provides ResolveURL.</description>
    <platform>all</platform>
    <assets><icon>icon.png</icon></assets>
  </extension>
</addon>
''')
icon = os.path.join(SRC, "plugin.video.KDubbed", "resources", "images", "icon.png")
if os.path.exists(icon):
    shutil.copy(icon, os.path.join(rdir, "icon.png"))

# 2. zip every add-on, collect addon.xml bodies
parts = []
for addon_id in sorted(os.listdir(SRC)):
    adir = os.path.join(SRC, addon_id)
    axml = os.path.join(adir, "addon.xml")
    if not os.path.isfile(axml):
        continue
    raw = open(axml, encoding="utf-8").read()
    version = ET.fromstring(raw.encode("utf-8")).get("version")
    out = os.path.join(ZIPS, addon_id)
    os.makedirs(out, exist_ok=True)
    zpath = os.path.join(out, f"{addon_id}-{version}.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for base, dirs, files in os.walk(adir):
            dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
            for fn in files:
                if fn.endswith((".pyc", ".pyo")):
                    continue
                full = os.path.join(base, fn)
                z.write(full, os.path.relpath(full, SRC))
    for extra in ("icon.png", "fanart.jpg"):
        for cand in (os.path.join(adir, extra), os.path.join(adir, "resources", "images", extra)):
            if os.path.exists(cand):
                shutil.copy(cand, os.path.join(out, extra))
                break
    parts.append(re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", raw).strip())
    print(f"built {zpath}")

# 3. addons.xml + md5 (md5 is computed from the exact bytes written)
body = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n' + "\n\n".join(parts) + "\n</addons>\n"
data = body.encode("utf-8")
open(os.path.join(ROOT, "addons.xml"), "wb").write(data)
open(os.path.join(ROOT, "addons.xml.md5"), "w").write(hashlib.md5(data).hexdigest())
ET.fromstring(data)  # sanity check
print("addons.xml ok, md5", hashlib.md5(data).hexdigest())


# 4. Plain HTML file lists so Kodi's File Manager can browse this repo as a
#    "source" when served by GitHub Pages (https://<owner>.github.io/<repo>/).
def write_index(folder, entries):
    links = "\n".join(f'<a href="{e}">{e}</a><br>' for e in entries)
    with open(os.path.join(folder, "index.html"), "w", encoding="utf-8") as f:
        f.write(f"<html><head><title>Index</title></head><body>\n{links}\n</body></html>\n")

repo_zip = f"{REPO_ID}-{REPO_VERSION}.zip"
shutil.copy(os.path.join(ZIPS, REPO_ID, repo_zip), os.path.join(ROOT, repo_zip))
for old in os.listdir(ROOT):  # drop older root copies of the repository zip
    if old.startswith(REPO_ID) and old.endswith(".zip") and old != repo_zip:
        os.remove(os.path.join(ROOT, old))
write_index(ROOT, [repo_zip, "zips/"])
write_index(ZIPS, sorted(d + "/" for d in os.listdir(ZIPS) if os.path.isdir(os.path.join(ZIPS, d))))
for d in os.listdir(ZIPS):
    full = os.path.join(ZIPS, d)
    if os.path.isdir(full):
        write_index(full, sorted(f for f in os.listdir(full) if f.endswith(".zip")))
open(os.path.join(ROOT, ".nojekyll"), "w").close()
print("index.html files written for GitHub Pages")
