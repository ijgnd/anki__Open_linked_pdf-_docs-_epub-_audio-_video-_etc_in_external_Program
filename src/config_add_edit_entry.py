import os
from pprint import pprint as pp

from anki.utils import (
    isMac,
    isWin
)

from aqt.qt import (
    QDialog,
    QFileDialog,
    Qt,

)
from aqt.utils import (
    askUser,
    getFile,
    showInfo,
    tooltip,
)

from .defaults_menu import (
    SelectDefault,
    guess_cmd_params,
)
from .helpers import (
    already_used_exts_for_others,
)

from .forms import config_dialog__add_edit_single_entry


class AddEditEntry(QDialog):
    def __init__(self, parent, thisconf, progs):
        if thisconf:
            self.thisconf = thisconf
        else:
            self.thisconf = {}
        self.progs = progs
        self.exts_used_when_opened = self.thisconf.get("extensions", [])
        self.parent = parent
        QDialog.__init__(self, parent, Qt.Window)
        self.dialog = config_dialog__add_edit_single_entry.Ui_Dialog()
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
        for e in self.dialog.le_extensions.text().split():
            if e in already_used_exts_for_others(self.progs, self.exts_used_when_opened):
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
    def __init__(self, parent=None, thisconf=None, progs=None):
        AddEditEntry.__init__(self, parent, thisconf, progs)
        self.dialog.wi_pdf.setVisible(False)  # hide until implemented


def gui_dialog(inst, thisconf=None, progs=None):
    # commented out since I made the internal pdf viewer into a separate extension.
    # if thisconf:
    #     if "extensions" in thisconf:
    #         p = thisconf["extensions"]
    #         if len(p) == 1 and p[0] == "pdf":
    #             return AddEditEntryPdf(inst, thisconf)
    return AddEditEntryRest(inst, thisconf, progs)
