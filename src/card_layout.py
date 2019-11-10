from pprint import pprint as pp

from anki.lang import _
from aqt.clayout import CardLayout
from aqt.utils import showInfo
from aqt.qt import *
from aqt import mw

from .consts import sep2, sep_merge
from .forms import addtofield


def gc(arg, fail=False):
    return mw.addonManager.getConfig(__name__).get(arg, fail)


def mySetupButtons(self):
    l = self.buttons = QHBoxLayout()
    help = QPushButton(_("Help"))
    help.setAutoDefault(False)
    l.addWidget(help)
    help.clicked.connect(self.onHelp)
    l.addStretch()
    onExtDocsLink = QPushButton(_("Ext-Docs-Link"))
    onExtDocsLink.setAutoDefault(False)
    l.addWidget(onExtDocsLink)
    onExtDocsLink.clicked.connect(self.onExtDocsLink)
    tm = ("This button belongs to the add-on 'Open linked pdf, docx, epub ... '."
          "For more info go to the add-on description on https://ankiweb.net/shared/addons/2.1.")
    onExtDocsLink.setToolTip(tm)
    addField = QPushButton(_("Add Field"))
    addField.setAutoDefault(False)
    l.addWidget(addField)
    addField.clicked.connect(self.onAddField)
    if not self._isCloze():
        flip = QPushButton(_("Flip"))
        flip.setAutoDefault(False)
        l.addWidget(flip)
        flip.clicked.connect(self.onFlip)
    l.addStretch()
    close = QPushButton(_("Close"))
    close.setAutoDefault(False)
    l.addWidget(close)
    close.clicked.connect(self.accept)
CardLayout.setupButtons = mySetupButtons


def onExtDocsLink(self):
    filefield = gc("field_for_filename", None)
    pagefield = gc("field_for_page", None)
    if not (filefield or pagefield):
        msg = ("Your setup for the Add-on 'Open linked pdf, docx, epub, audio/video, "
               "etc. in external Program' is not valid.\n\n"
               "Check the add-on configuration and set the fieldnames for "
               "'field_for_filename' and 'field_for_page'.")
        showInfo(msg)
        return
    fieldnames = [f['name'] for f in self.model['flds']]
    if filefield not in fieldnames or pagefield not in fieldnames:
        msg = ("Your setup for the Add-on 'Open linked pdf, docx, epub, audio/video, "
               "etc. in external Program' is not valid.\n\n"
               "Your notetype doesn't contain fields with the names %s and %s"
               "which you set in the config of this add-on. Either adjust the config"
               "of this add-on or add fields with these names to this note type.\n\n"
               "If you don't know what I mean by 'add fields to your note type' watch"
               "this video https://www.youtube.com/watch?v=JTKqd4nqsK0&feature=youtu.be&t=22" % (
                   filefield, pagefield
               ))
        showInfo(msg)
        return
    diag = QDialog(self)
    form = addtofield.Ui_Dialog()
    form.setupUi(diag)
    form.linktext.setText("View external file: {{text:%s}}" % filefield)
    form.font.setCurrentFont(QFont("Arial"))
    form.size.setValue(20)
    diag.show()
    if not diag.exec_():
        return
    if form.radioQ.isChecked():
        obj = self.tform.front
    else:
        obj = self.tform.back
    t = obj.toPlainText()
    lt = form.linktext.text()
    t += (f"""<br><br><a href='javascript:pycmd("{sep_merge}{{{{text:{filefield}}}}}"""
          f"""{sep2}{{{{text:{pagefield}}}}}");'>{lt}</a>"""
          )
    obj.setPlainText(t)
    self.saveCard()
CardLayout.onExtDocsLink = onExtDocsLink
