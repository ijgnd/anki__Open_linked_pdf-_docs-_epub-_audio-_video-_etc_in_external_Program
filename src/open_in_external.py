"""
Add-on for Anki 2.1: Open linked pdf, docs, epub, audio, video, etc in external Program

Copyright: (c) 2019- ijgnd

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import subprocess
import shlex
import getpass

from anki.hooks import addHook, wrap
from aqt import mw
from aqt.reviewer import Reviewer
from aqt.browser import Browser
from aqt.utils import tooltip
from anki.utils import isWin


def gc(arg, fail=False):
    return mw.addonManager.getConfig(__name__).get(arg, fail)


# make settings importable into additional card fields add-on
# I don't want to replicate its code here for future maintainability
field_for_filename = ""
field_for_page = ""
def setFolders():
    global field_for_filename
    global field_for_page
    field_for_filename = gc("field_for_filename", "")
    field_for_page = gc("field_for_page", "")
addHook('profileLoaded', setFolders)


def open_external(file, page):
    if file.startswith("file://") and isWin:  # on linux these files don't seem to pose a problem
        file = file[8:]
    ext = os.path.splitext(file)[1][1:].lower()
    for v in gc("programs_for_extensions").values():
        if "extensions" in v:    # "other_extensions" doesn't have this key
            if ext in v["extensions"]:
                if not os.path.isabs(file):
                    username = getpass.getuser()
                    base = v["default_folder_for_relative_paths"].replace("MY_USER", username)
                    if not base:
                        tooltip("invalid settings for the add-on 'Open linked pdf, ...'. Aborting")
                    file = os.path.join(base, file)
                if not os.path.exists(file):
                    s = "file '%s' doesn't exist. maybe adjust the config or field values" % file
                    tooltip(s)
                    return
                if page and "command_open_on_page_arguments" in v:
                    a = (v["command_open_on_page_arguments"]
                           .replace("PATH", '"' + file + '"')
                           .replace("PAGE", page)
                           )
                    cmd = '"' + v["command"] + '" ' + a
                else:
                    cmd = '"' + v["command"] + '" ' + ' "' + file + '"'
                if isWin == 'win32':
                    args = cmd
                else:
                    args = shlex.split(cmd)
                subprocess.Popen(args)
                return


def myLinkHandler(self, url, _old):
    if url.startswith("open_external_filesüöäüöä"):
        file, page = url.replace("open_external_filesüöäüöä", "").split("üöäüöä")
        open_external(file, page)
    else:
        return _old(self, url)
Reviewer._linkHandler = wrap(Reviewer._linkHandler, myLinkHandler, "around")
