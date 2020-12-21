import json
import os
from collections import OrderedDict
from pprint import pprint as pp

from aqt import mw
from aqt.qt import (
    QAbstractItemView,
    QAbstractScrollArea,
    QCursor,
    QDialog,
    QHeaderView,
    QMenu,
    QTableView,
    QTableWidgetItem,
)
from aqt.utils import (
    askUser,
    getFile,
    getSaveFile,
    showInfo,
    tooltip
)

from .config import (
    gc,
)
from .config_add_edit_entry import (
    gui_dialog,
)
from .forms import config_main


class AddonConfigWindow(QDialog):
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

        self.mcw.le_prefix.setVisible(False)
        self.mcw.ql_prefix.setVisible(False)
        self.mcw.le_sep.setVisible(False)
        self.mcw.ql_sep.setVisible(False)
        self.mcw.le_prefix.setText(gc("inline_prefix", ""))
        self.mcw.le_sep.setText(gc("inline_separator", ""))
        self.mcw.cb_extended.setText("enable experimental feature (check the ankiweb description for details)")
        self.mcw.cb_extended.stateChanged.connect(self.on_extended_changed)
        if gc("inline_prefix"):
            self.mcw.cb_extended.setChecked(True)

    def on_extended_changed(self):
        tooltip("Restart Anki so that the changes take effect.")
        # at the moment there's no customization
        """
        if self.mcw.cb_extended.isChecked():
            self.mcw.le_prefix.setVisible(True)
            self.mcw.ql_prefix.setVisible(True)
            self.mcw.le_sep.setVisible(True)
            self.mcw.ql_sep.setVisible(True)
        else:
            self.mcw.le_prefix.setVisible(False)
            self.mcw.ql_prefix.setVisible(False)
            self.mcw.le_sep.setVisible(False)
            self.mcw.ql_sep.setVisible(False)
            self.mcw.le_prefix.setText("")
            self.mcw.le_sep.setText("")
        """

    def set_attribute_progs(self):
        progs = gc("programs_for_extensions", "")
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
        self.mcw.le_field_for_filename.setText(gc("field_for_filename", ""))
        self.mcw.le_field_for_page.setText(gc("field_for_page", ""))
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

        # at the moment there's no customization
        # self.config["inline_prefix"] = self.mcw.le_prefix.text()
        # self.config["inline_separator"] = self.mcw.le_sep.text()
        if self.mcw.cb_extended.isChecked(): 
            self.config["inline_prefix"] = "____"
            self.config["inline_separator"] = "___"
            self.config["context menu entries in reviewer"] = True
            self.config["context menu entries in editor"] = True
            self.config["make inline prefiexed clickable"] = True
        else:
            self.config["inline_prefix"] = ""
            self.config["inline_separator"] = ""
            self.config["context menu entries in reviewer"] = False
            self.config["context menu entries in editor"] = False
            self.config["make inline prefiexed clickable"] = False

    def onReject(self):
        self.reject()

    def onAccept(self):
        self.update_config()
        self.accept()
