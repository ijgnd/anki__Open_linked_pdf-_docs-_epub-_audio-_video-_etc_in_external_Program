import os

from aqt import mw

def gc(arg, fail=False):
    try:
        out = mw.addonManager.getConfig(__name__).get(arg, fail)
    except:
        return None
    else:
        return out


from anki import version as anki_version
_, _, point = anki_version.split(".")
pointversion = int(point)

addon_path = os.path.dirname(__file__)

pycmd_string = "open_external_addon"
