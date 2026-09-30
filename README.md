# Khmer Kodi (personal) repository

Kodi repository for the maintained **Khmer Dubbed** add-on (`plugin.video.KDubbed`).

## Install (once per Kodi device)
1. Kodi → Settings → System → Add-ons → turn on **Unknown sources**.
2. Add-ons → Install from zip file → `zips/repository.khmerkodi.personal/repository.khmerkodi.personal-1.0.0.zip`.
3. Add-ons → Install from repository → *Khmer Kodi (personal) Repository* → Video add-ons → **Khmer Dubbed**.

After that, Kodi updates Khmer Dubbed automatically whenever a newer version is pushed here.

## Publishing a fix
1. Edit the add-on under `src/plugin.video.KDubbed/` and bump `version` in its `addon.xml`.
2. `python3 build_repo.py <owner> <repo>`
3. Commit and push. Kodi checks repositories roughly once a day (or on start-up).
