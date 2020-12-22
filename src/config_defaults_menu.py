import copy
import os
from pprint import pprint as pp

from anki.utils import (
    isLin,
    isMac,
    isWin
)
from aqt import mw
from aqt.qt import *
from aqt.utils import (
    askUser,
    tooltip
)

from .default_settings_for_progs.py import (
    tpl_pdf,
    tpl_office,
    tpl_vlc,
    tpl_ebook,
    tpl_fp,
    tpl_py,
    tpl_zim,
    tpl_browser
)
from .forms import select_default


win_bin_paths = ["C:\\Program Files",
                 "C:\\Program Files (x86)", 
                 os.getenv('APPDATA'),
                 os.path.expandvars("%LocalAppData%"),
                 ]


class SelectDefault(QDialog):
    def __init__(self, parent=None):
        self.parent = parent
        QDialog.__init__(self, parent, Qt.Window)
        self.dialog = select_default.Ui_Dialog()
        self.dialog.setupUi(self)
        self.options = {
            "PDF": tpl_pdf,
            "Office Documents like doc, docx, odt": tpl_office,
            "Audio and Video files with vlc": tpl_vlc,
            "ebooks (epub/mobi)": tpl_ebook,
            "mindmap with freeplane": tpl_fp,
            "local html files with your Browser": tpl_browser,
        }
        self.dialog.list_defaults.addItems(self.options.keys())
        self.dialog.list_defaults.itemDoubleClicked.connect(self.onAccept)
        self.dialog.buttonBox.accepted.disconnect(self.accept)
        self.dialog.buttonBox.accepted.connect(self.onAccept)
        self.dialog.buttonBox.rejected.disconnect(self.reject)
        self.dialog.buttonBox.rejected.connect(self.onReject)
        self.thisconfig = {}

    def onReject(self):
        tooltip('reject')
        self.reject()

    def onAccept(self):
        sel = self.dialog.list_defaults.currentItem().text()
        template = self.options[sel]
        self.thisconfig = copy.deepcopy(template)
        cmd, param = guess_cmd_params(self, self.thisconfig["extensions"])
        # also write empty values to make sure that no old values remain
        self.thisconfig["command"] = cmd
        self.thisconfig["command_open_on_page_arguments"] = param
        QDialog.accept(self)


def process_dir(mypath, searchterm):
    thislist = []
    for root, dirs, files in os.walk(mypath):
        for file in files:
            if file.endswith(searchterm):
                thislist.append(os.path.join(root, file))
    return thislist


def get_full_paths_for_templates(winlist, maclist, linuxlist):
    # shutil.which?
    if isLin:
        lpv = copy.deepcopy(linuxlist)
        for k, v in lpv.items():
            # for known_pdf_viewers_lin for "full paths" values I don't need a dict
            # but I use a dict with one entry so that I don't need to check in guess_cmd_params
            # if "full paths" is a dict or not.
            for e in v["full paths"]:
                if not os.path.exists(e):
                    v["full paths"] = None
        return {k: v for k, v in lpv.items() if v["full paths"] is not None}
    elif isMac:
        return {}  # "open -a Preview.app" doesn't help since a) open doesn't take parameters for
        # pages and b) Preview.app doesn't support cli parameters (some programs when
        # called from their actual location do take parmeters), see e.g.
        # https://apple.stackexchange.com/questions/233945/opening-a-specific-page-on-mac-preview-from-terminal
    else:  # isWin
        kpv = copy.deepcopy(winlist)
        winwarning = (
"Detecting the paths of suitable pdf viewers on Windows takes some time. This add-on will "
"search your program folders and your Appdata folder. If you have a lot of software installed "
"and don't have a SSD this might take minutes. If you don't want to wait that long click 'No' "
"to abort. Then you must set the paths manually.\n\n"
"My approach can't detect programs that are installed from the Windows Store. Their paths "
"are usually well hidden and they often do not take cli arguments that I need to pass the "
"file to open and the page to open.\n\n"
"I just search for common names of executables. This means I might also get false positives. "
"You must check the suggested path if it looks like it belongs to a legitimate app and that I "
"didn't match some malicious executable from your tempfolder ...\n\n\n"
"Technical background: This technical information is not necessary. It is included for two "
"reasons:\n"
"- Maybe someone with experience in programming Windows reads this and tells me what I missed "
"so that this add-on can be improved in the future.\n"
"- Anticipate likely complaints. This add-on can only use python components that are built-into "
"Anki. Anki does not ship the full python standard library. So I can't use the module 'winreg'. "
"When it comes to detecting installed programs for a filetype the common suggestion seems to be "
"to check the registry key 'HKCU ... FileExts\\.pdf\\OpenWithList'. But this doesn't include "
"all pdf viewers and also not all viewers are in PATH.\n\n\n"
"Proceed?"
)
        if askUser(winwarning, defaultno=True):
            mw.progress.start(immediate=True)
            try:
                for k, v in kpv.items():
                    v["full paths"] = []
                    for e in v["executable names"]:
                        for p in win_bin_paths:
                            v["full paths"].extend(process_dir(p, e))
                    # remove empty
            finally:
                mw.progress.finish()
            return {k: v for k, v in kpv.items() if v["full paths"] is not None}


class SelectFromMultiple(QDialog):
    def __init__(self, parent=None, entries=[]):
        self.parent = parent
        QDialog.__init__(self, parent, Qt.Window)
        self.dialog = select_default.Ui_Dialog()
        self.dialog.setupUi(self)
        self.setWindowTitle("Anki Add-on: Select binary")
        self.dialog.list_defaults.addItems(entries)
        self.dialog.list_defaults.itemDoubleClicked.connect(self.onAccept)
        self.dialog.buttonBox.accepted.disconnect(self.accept)
        self.dialog.buttonBox.accepted.connect(self.onAccept)

    def onAccept(self):
        self.selec = self.dialog.list_defaults.currentItem().text()
        self.accept()


def process_multiple(inst, vdict):
    dialog_entries = []
    return_dict = {}
    for k, v in vdict.items():
        for i in v["full paths"]:
            text = k + '   (' + i + ')'
            dialog_entries.append(text)
            return_dict[text] = [i, v["pageparams"]]
    d = SelectFromMultiple(inst, dialog_entries)
    if d.exec():
        for k, v in return_dict.items():
            if k == d.selec:
                return v[0], v[1]


def guess_cmd_params_helper(inst, winlist, maclist, linuxlist):
    vdict = get_full_paths_for_templates(winlist, maclist, linuxlist)
    if vdict:
        lc = len(vdict.keys())
        if lc == 0:
            return "", ""
        elif lc == 1:
            d = next(iter(vdict.values()))
            if len(d["full paths"]) == 0:
                return "", ""
            elif len(d["full paths"]) == 1:
                return d["full paths"][0], d["pageparams"]
            else:
                process_multiple(inst, vdict)
        else:
            return process_multiple(inst, vdict)
    else:
        return "", ""


def guess_cmd_params(inst, exts):
    ali = [
        # [listOfExts, DictProgsWin, DictProgsMac, DictProgsLinux]
        [["pdf"],                   tpl_pdf["progs_win"],     None, tpl_pdf["progs_lin"]],
        [tpl_vlc["extensions"],     tpl_vlc["progs_win"],     None, tpl_vlc["progs_lin"]],
        [tpl_office["extensions"],  tpl_office["progs_win"],  None, tpl_office["progs_lin"]],
        [tpl_ebook["extensions"],   tpl_ebook["progs_win"],   None, tpl_ebook["progs_lin"]],
        [tpl_fp["extensions"],      tpl_fp["progs_win"],      None, tpl_fp["progs_lin"]],
        [tpl_py["extensions"],      tpl_py["progs_win"],      None, tpl_py["progs_lin"]],
        [tpl_zim["extensions"],     tpl_zim["progs_win"],     None, tpl_zim["progs_lin"]],
        [tpl_browser["extensions"], tpl_browser["progs_win"], None, tpl_browser["progs_lin"]],
    ]
    out1, out2 = "", ""
    for e in ali:
        crit = [i for i in exts if i in e[0]]
        if crit:
            out1, out2 = guess_cmd_params_helper(inst, e[1], e[2], e[3])
    return out1, out2
