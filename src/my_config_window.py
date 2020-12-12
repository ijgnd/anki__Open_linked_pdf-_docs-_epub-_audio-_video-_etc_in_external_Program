import json
import os
from collections import OrderedDict
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
    getFile,
    getSaveFile,
    showInfo,
    tooltip
)

from .defaults_menu import *
from .forms import config_main
from .forms import thisconfdialog


class AddEditEntry(QDialog):
    def __init__(self, parent, thisconf):
        if thisconf:
            self.thisconf = thisconf
        else:
            self.thisconf = {}
        self.parent = parent
        self.set_exts_used_for_other_progs()
        QDialog.__init__(self, parent, Qt.Window)
        self.dialog = thisconfdialog.Ui_Dialog()
        self.dialog.setupUi(self)
        self.adjustSize()
        self.fill_fields()
        self.dialog.pb_load_from_defaults.clicked.connect(self.load_from_defaults)
        self.dialog.pb_path_add.clicked.connect(self.add_default_path)
        self.dialog.pb_path_up.clicked.connect(self.path_up)
        self.dialog.pb_path_down.clicked.connect(self.path_down)
        self.dialog.pb_path_del.clicked.connect(self.del_default_path)
        self.dialog.pb_cmd_pickpath.clicked.connect(self.pickcmdpath)
        self.dialog.pb_cmd_guess.clicked.connect(self.cmdguess)
        self.dialog.pb_parameters_guess.clicked.connect(self.parameters_guess)
        self.dialog.buttonBox.accepted.disconnect(self.accept)
        self.dialog.buttonBox.accepted.connect(self.onAccept)
        self.dialog.buttonBox.rejected.disconnect(self.reject)
        self.dialog.buttonBox.rejected.connect(self.onReject)
        self.dialog.buttonBox.helpRequested.connect(self.onHelp)
        self.dialog.pb_parameters_guess.hide()
        self.dialog.pb_params_info.clicked.connect(self.onParamsInfo)
    
    def onParamsInfo(self):
        infmsg = ("PAGE will be replaced with the contents of the field 'field_for_page' and "
                  "PATH will be replaced with the contents of the field 'field_for_filename' "
                  "when clicking the hyperlink during review or running this add-on from the "
                  "editor context menu.")
        showInfo(infmsg)
    
    def set_exts_used_for_other_progs(self):
        a = set(self.parent.config["extensions_all"])
        if "extensions" in self.thisconf:
            b = set(self.thisconf["extensions"])
            self.exts_used_for_other_progs = list(a-b)
        else:
            self.exts_used_for_other_progs = list(a)

    def fill_fields(self):
        if not self.thisconf:
            self.dialog.wi_pdf.setVisible(False)
            self.adjustSize()
        if self.thisconf:
            if "comment" in self.thisconf:
                self.dialog.le_comment.setText(self.thisconf["comment"])
            if "default_folder_for_relative_paths" in self.thisconf:
                path = self.thisconf["default_folder_for_relative_paths"]
                if isinstance(path, str):
                    self.dialog.lw_paths.addItem(path)
                else:
                    self.dialog.lw_paths.addItems(path)
            if "extensions" in self.thisconf:
                p = self.thisconf["extensions"]
                if not (len(p) == 1 and p[0] == "pdf"):
                    self.dialog.wi_pdf.setVisible(False)
                    self.adjustSize()
            def maybe_set_exts():
                if "extensions" in self.thisconf:
                    exts = " ".join(self.thisconf["extensions"])
                    self.dialog.le_extensions.setText(exts)
            if "extensions_fixed" in self.thisconf:
                if self.thisconf["extensions_fixed"]:
                    maybe_set_exts()
                    self.dialog.le_extensions.setReadOnly(True)
                    self.dialog.le_extensions.setStyleSheet("background-color: rgb(239, 240, 241);")
                    self.dialog.ql_exts.setText("Extensions (not changeable)")
                else:
                    maybe_set_exts()
            else:
                maybe_set_exts()
            if "command" in self.thisconf:
                self.dialog.le_cmd.setText(self.thisconf["command"])
            if "command_open_on_page_arguments" in self.thisconf:
                self.dialog.le_parameters.setText(self.thisconf["command_open_on_page_arguments"])

    def load_from_defaults(self):
        e = SelectDefault(self)
        if e.exec_():
            if e.thisconfig:
                text = ("This will overwrite all the values in the current window.\n\n"
                        "If you don't want this abort and re-run this command from a new "
                        "and empty window (in the main config window click on "
                        "'Add program/extension').")
                if askUser(text, defaultno=True):
                    self.thisconf = e.thisconfig
                    self.fill_fields()

    def add_default_path(self):
        dir = QFileDialog.getExistingDirectory(None, 'Anki Add-on Select a folder:',
                                               os.path.expanduser("~"), QFileDialog.ShowDirsOnly)
        if dir:
            self.dialog.lw_paths.addItems([dir])

    def del_default_path(self):
        listwidget = self.dialog.lw_paths
        sel = listwidget.selectedItems()
        if not sel:
            return
        for item in sel:
            listwidget.takeItem(listwidget.row(item))

    def path_up(self):
        self.move_active(-1)
    
    def path_down(self):
        self.move_active(1)

    def move_active(self, direction):
        listwidget = self.dialog.lw_paths
        currentRow = listwidget.currentRow()
        currentItem = listwidget.takeItem(currentRow)
        newpos = currentRow + direction
        if newpos < 0:
            newpos = 0
        if newpos > listwidget.count():
            newpos = listwidget.count()
        listwidget.insertItem(newpos, currentItem)
        listwidget.setCurrentRow(newpos)

    def pickcmdpath(self):
        # mod of aqt.utils getFile
        d = QFileDialog()
        mode = QFileDialog.ExistingFile
        d.setFileMode(mode)
        if isWin:
            d.setDirectory("C:\\")
        if isMac:
            d.setDirectory("/Applications")
        else:
            d.setDirectory(os.path.expanduser("~"))
        d.setWindowTitle("Anki Add-on: Select Executable")
        if d.exec():
            self.dialog.le_cmd.setText(d.selectedFiles()[0])

    def cmdguess(self):
        exts = self.dialog.le_extensions.text().split()
        if not exts:
            tooltip("no entry in extensions.")
            return
        if not type(exts) == list:
            tooltip("no entry in extensions.")
            return
        if not len(exts) >= 1:
            tooltip("no entry in extensions.")
            return
        cmd, params = guess_cmd_params(self, exts)
        if not cmd:
            showInfo("Guessing failed. You need to set the command and parameters manually.")
        else:
            if type(cmd) == str:
                self.dialog.le_cmd.setText(cmd)
            else:
                showInfo('144 problem')
            # if type(cmd) == list:
            #     if len(cmd) == 1:
            #         self.dialog.le_cmd.setText(cmd[0])
        if params:
            if type(params) == str:
                if not self.dialog.le_parameters.text().strip() == "":
                    if not askUser("The field 'command parameters to open on specific page' "
                                   "doesn't appear to be empty. Overwrite?"):
                        return
                self.dialog.le_parameters.setText(params)

    def parameters_guess(self):
        tooltip('not yet implemented')

    def onReject(self):
        QDialog.reject(self)

    def onHelp(self):
        tooltip('not implemented yet: on help')

    def onAccept(self):
        if "pinned" in self.thisconf:
            pinned = self.thisconf["pinned"]
        else:
            pinned = False
        if "extensions_fixed" in self.thisconf:
            ext_fixed = self.thisconf["extensions_fixed"]
        else:
            ext_fixed = False
        exts = self.dialog.le_extensions.text().split()
        for e in exts:
            if e in self.exts_used_for_other_progs:
                usedmsg = ("You listed an extension here that's already assigned to a different"
                           "command/program. Please remove '%s' from the 'Extensions'.\n\n"
                           "Returning back to the config window.\n\n"
                           "If you now want to use '%s' for the command/program in this window "
                           "nevertheless remove '%s' from 'Extensions'. Then you can close this "
                           "window. Then modify the other command/program and delete '%s' "
                           "and then modify this command/program and add '%s' to 'Extensions'."
                           % (e, e, e, e, e)
                           )
                showInfo(usedmsg)
                return
        self.newsetting = {
            "comment":  self.dialog.le_comment.text(),
            "default_folder_for_relative_paths": [str(self.dialog.lw_paths.item(i).text()) for i in range(self.dialog.lw_paths.count())],
            "extensions": self.dialog.le_extensions.text().split(),
            "command": self.dialog.le_cmd.text().strip(),
            "command_open_on_page_arguments": self.dialog.le_parameters.text(),
            "pinned": pinned,
            "extensions_fixed": ext_fixed,
        }
        self.accept()


class AddEditEntryPdf(AddEditEntry):
    def __init__(self, parent=None, thisconf=None):
        AddEditEntry.__init__(self, parent, thisconf)
        self.dialog.wi_pdf.setVisible(False)  # hide until implemented
        if "command" in self.thisconf:
            if self.thisconf["command"] == "INTERNAL":
                self.dialog.cb_pdf_usepdfjs.setChecked(True)
                self.on_enable_internal()
        else:
            self.dialog.cb_pdf_usepdfjs.setChecked(True)
            self.on_enable_internal()
        self.dialog.cb_pdf_usepdfjs.stateChanged.connect(self.onTogglePdfjs)
        pdfmsg = ("see ___bak_")
        self.dialog.ql_pdf_explan_internal_or_external.setText(pdfmsg)
        self.resize(1090, 481)

    def onTogglePdfjs(self):
        if self.dialog.cb_pdf_usepdfjs.isChecked():
            self.on_enable_internal()
        else:
            self.on_disable_internal()

    def on_enable_internal(self):
        # this doesn't help self.thisconf["command"] = "INTERNAL" since in the parent's method
        # accept the attribute newsettings doesn't read thisconf
        self.dialog.le_cmd.setText("INTERNAL")
        self.dialog.wi_cmds.setVisible(False)
        self.adjustSize()

    def on_disable_internal(self):
        self.dialog.wi_cmds.setVisible(True)
        self.adjustSize()


class AddEditEntryRest(AddEditEntry):
    def __init__(self, parent=None, thisconf=None):
        AddEditEntry.__init__(self, parent, thisconf)
        self.dialog.wi_pdf.setVisible(False)  # hide until implemented


def gui_dialog(inst, thisconf=None):
    # commented out since I made the internal pdf viewer into a separate extension.
    # if thisconf:
    #     if "extensions" in thisconf:
    #         p = thisconf["extensions"]
    #         if len(p) == 1 and p[0] == "pdf":
    #             return AddEditEntryPdf(inst, thisconf)
    return AddEditEntryRest(inst, thisconf)


class MyConfigWindow(QDialog):
    def __init__(self, c):
        parent = mw.app.activeWindow()
        QDialog.__init__(self, parent)
        self.config = c
        self.mcw = config_main.Ui_Dialog()
        self.mcw.setupUi(self)
        self.setWindowTitle("Anki: Change Options for Add-on 'open external'")
        self.mcw.pb_more.clicked.connect(self.onMore)
        self.mcw.pb_add.clicked.connect(self.onAdd)
        self.mcw.pb_delete.clicked.connect(self.onDelete)
        self.mcw.pb_modify.clicked.connect(self.onModify)
        self.init_table()
        self.set_attribute_progs()
        self.set_contents()
        self.adjustSize()
        self.mcw.buttonBox.accepted.disconnect(self.accept)
        self.mcw.buttonBox.accepted.connect(self.onAccept)
        self.mcw.buttonBox.rejected.disconnect(self.reject)
        self.mcw.buttonBox.rejected.connect(self.onReject)

    def gc(self, arg, fail=False):
        return self.config.get(arg, fail)

    def set_attribute_progs(self):
        progs = self.gc("programs_for_extensions", "")
        msg = ('error in config of the add-on: Open linked pdf.\n'
               'Not reading the config of the add-on')
        if not progs:
            self.progs = []
        else:
            if isinstance(progs, list):
                for i in progs:
                    if not isinstance(i, dict):
                        showInfo(msg)
                        self.progs = []
                        break
                self.progs = sorted(progs, key=lambda k: k['comment'])
            else:
                self.progs = []
                showInfo(msg)

    def init_table(self):
        headers = [("comment", "comment"),
                   ("extensions", "extensions"),
                   ("command", "command/program"),
                   ("command_open_on_page_arguments", "command open on page arguments"),
                   ("default_folder_for_relative_paths", "default folder for relative paths"),
                   ]
        self.tableHeaders = OrderedDict(headers)
        self.mcw.tw.itemDoubleClicked.connect(self.ondoubleclick)

    def set_contents(self):
        self.mcw.le_field_for_filename.setText(self.gc("field_for_filename", ""))
        self.mcw.le_field_for_page.setText(self.gc("field_for_page", ""))
        widget = self.mcw.tw
        widget.setSelectionBehavior(QTableView.SelectRows)
        widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        widget.setRowCount(len(self.progs))
        widget.setColumnCount(len(self.tableHeaders))
        widget.setHorizontalHeaderLabels(self.tableHeaders.values())
        widget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        widget.resizeColumnsToContents()
        widget.verticalHeader().setVisible(False)
        widget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch) # ResizeToContents
        widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)   # Stretch
        # per column https://stackoverflow.com/q/38098763
        widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        # workaround for QTableWidget: add empty strings to all fields to make them clickable
        for i in range(len(self.progs)):
            for j in range(len(self.tableHeaders)):
                newitem = QTableWidgetItem(str(" "))
                widget.setItem(j, i, newitem)

        for a, b in enumerate(self.progs):
            for k, v in b.items():
                try:
                    index = list(self.tableHeaders.keys()).index(k)
                except ValueError:
                    pass
                    # config value not shown in table e.g. "fixed"
                else:
                    newitem = QTableWidgetItem(str(v))
                    widget.setItem(a, index, newitem)

    def modify_helper(self, row):
        thisconf = self.progs[row]
        e = gui_dialog(self, thisconf=thisconf)
        if e.exec():
            self.progs[row] = e.newsetting
            self.progs = sorted(self.progs, key=lambda k: k['comment'])
            self.set_contents()

    def ondoubleclick(self, item):
        row = item.row()
        self.modify_helper(row)

    def onModify(self):
        try:
            row = self.mcw.tw.currentRow()
        except:
            row = -1
        if row != -1:
            self.modify_helper(row)
        else:
            tooltip("No row selected.")

    def update_all_exts(self):
        allexts = []
        for e in self.progs:
            for v in e["extensions"]:
                if e not in allexts:
                    allexts.append(v)
        self.config["extensions_all"] = allexts

    def onAdd(self):
        e = gui_dialog(self, thisconf=None)
        if e.exec_():
            self.progs.append(e.newsetting)
            self.progs = sorted(self.progs, key=lambda k: k['comment'])
            self.set_contents()
            self.adjustSize()
            self.update_all_exts()

    def onDelete(self):
        try:
            row = self.mcw.tw.currentRow()
        except:
            tooltip("No row selected.")
            return
        if row != -1:
            if self.progs[row]["pinned"]:
                tooltip("This row/setting can't be deleted.")
                return
            else:
                text = "Delete row number %s" % str(row+1)
                if askUser(text, defaultno=True):
                    del self.progs[row]
                    self.set_contents()
                    self.adjustSize()

    def onMore(self):
        m = QMenu(mw)
        a = m.addAction("Delete Config and Rebuilt")
        a.triggered.connect(self.onRebuilt)
        a = m.addAction("Export config to json")
        a.triggered.connect(self.onExport)
        a = m.addAction("Import config from json")
        a.triggered.connect(self.onImport)
        m.exec_(QCursor.pos())

    def onExport(self):
        o = getSaveFile(mw, title="Anki - Select file to save the add-on config to",
                        dir_description="jsonbuttons",
                        key=".json",
                        ext=".json",
                        fname="Open_linked_pdf_docx_epub_audiovideo_in_external_Program.json"
                        )
        if o:
            with open(o, 'w') as fp:
                self.update_config()
                json.dump(self.config, fp)

    def onImport(self):
        o = getFile(self, "Anki - Read config for add-on from file", None, "json",
                            key="json", multi=False)
        if o:
            try:
                with open(o, 'r') as fp:
                    c = json.load(fp)
            except:
                showInfo("Aborting. Error while reading file.")
            try:
                self.config = c
            except:
                showInfo("Aborting. Error in file.")
            else:
                self.set_contents()
                self.adjustSize()

    def onRebuilt(self):
        msg = ("Delete your setup and restore default config?\n\n"
               "You should consider to export your current config first.")
        if askUser(msg, defaultno=False):
            self.config = mw.addonManager.addonConfigDefaults(__name__.split(".")[0])
            self.set_attribute_progs()
            self.set_contents()
            self.adjustSize()

    def update_config(self):
        # relevant for onExport/backup
        self.config["field_for_filename"] = self.mcw.le_field_for_filename.text()
        self.config["field_for_page"] = self.mcw.le_field_for_page.text()
        self.config["programs_for_extensions"] = self.progs

    def onReject(self):
        self.reject()

    def onAccept(self):
        self.update_config()
        self.accept()
