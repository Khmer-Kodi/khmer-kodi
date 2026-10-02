import os
def translatePath(p):
    base = os.environ.get("KODI_HOME", "/tmp/kodi_stub_home")
    return os.path.join(base, p.split("//", 1)[-1].replace("/", os.sep))
