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
from anki.utils import (
    isLin,
    isWin,
    stripHTML
)
from aqt import mw
from aqt.reviewer import Reviewer
from aqt.browser import Browser
from aqt.utils import tooltip

from .config import gc
from .consts import sep2, sep_merge


def open_external(file, page):
    if file.startswith("file://"):
        if isWin:
            file = file[8:]
        else:
            file = file[7:]
    ext = os.path.splitext(file)[1][1:].lower().rstrip()
    for v in gc("programs_for_extensions"):
        if v.get("extensions"):    # "other_extensions" doesn't have this key
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
                # temporary workaround for INTERNAL for pdf
                if v["command"].lower() == "internal":
                    tooltip('INTERNAL selected. Not implemented yet. Aborting ...')
                    return
                if page and v.get("command_open_on_page_arguments"):
                    a = (v["command_open_on_page_arguments"]
                           .replace("PATH", '"' + file + '"')
                           .replace("PAGE", page)
                           )
                    cmd = '"' + v["command"] + '" ' + a
                else:
                    cmd = '"' + v["command"] + '" ' + ' "' + file + '"'
                if isWin:
                    args = cmd
                else:
                    args = shlex.split(cmd)
                if isLin:
                    env = os.environ.copy()
                    toremove = ['LD_LIBRARY_PATH', 'QT_PLUGIN_PATH', 'QML2_IMPORT_PATH']
                    for e in toremove:
                        env.pop(e, None)
                    subprocess.Popen(args, env=env)
                else:
                    subprocess.Popen(args)
                return


def myLinkHandler(self, url, _old):
    if url.startswith(sep_merge):
        file, page = url.replace(sep_merge, "").split(sep2)
        open_external(file, page)
    else:
        return _old(self, url)
Reviewer._linkHandler = wrap(Reviewer._linkHandler, myLinkHandler, "around")


def myhelper(editor, menu):
    filefld = [f["ord"] for f in editor.note.model()['flds'] if f['name'] == gc("field_for_filename")]
    if not filefld:
        return
    file = stripHTML(editor.note.fields[filefld[0]])
    if not file:
        # field is empty
        return
    pagefld = [f["ord"] for f in editor.note.model()['flds'] if f['name'] == gc("field_for_page")]
    if pagefld:
        page = stripHTML(editor.note.fields[pagefld[0]])
    a = menu.addAction("open %s" % gc("field_for_filename"))
    a.triggered.connect(lambda _, f=file, p=page: open_external(f, p))


def add_to_context(view, menu):
    e = view.editor
    field = e.currentField
    # with glutanimate's spell checker e.saveNow doesn't work
    try:
        spellchecker = __import__("spell_checker").spellcheck
    except:
        if field:
            e.saveNow(lambda ed=e, m=menu: myhelper(ed, m))
        else:
            myhelper(e, menu)
    else:
        myhelper(e, menu)
addHook("EditorWebView.contextMenuEvent", add_to_context)
