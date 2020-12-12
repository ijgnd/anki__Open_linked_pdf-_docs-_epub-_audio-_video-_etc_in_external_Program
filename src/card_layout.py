from pprint import pprint as pp
import uuid

from anki.hooks import wrap
from aqt.clayout import CardLayout
from aqt.utils import showInfo
from aqt.qt import *
from aqt import mw

from .config import gc, pointversion
from .consts import sep2, sep_merge
if pointversion < 28:
    from .forms import addtofield
else:
    from .forms import addtofield28 as addtofield



def mySetupButtons(self):
    onExtDocsLink = QPushButton("Ext-Docs-Link")
    onExtDocsLink.setAutoDefault(False)
    self.buttons.insertWidget(3, onExtDocsLink)
    onExtDocsLink.clicked.connect(self.onExtDocsLink)
    tm = ("This button belongs to the add-on 'Open linked pdf, docx, epub ... '."
          "For more info go to the add-on description on https://ankiweb.net/shared/addons/2.1.")
    onExtDocsLink.setToolTip(tm)
CardLayout.setupButtons = wrap(CardLayout.setupButtons, mySetupButtons)


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
    form.le_linktext.setText("View external file: {{text:%s}}" % filefield)
    form.le_fieldname.setText(filefield)
    form.le_page.setText(pagefield)
    form.font.setCurrentFont(QFont("Arial"))
    form.size.setValue(20)
    diag.show()
    if not diag.exec_():
        return
    if pointversion < 28:
        if form.radioQ.isChecked():
            obj = self.tform.front
        else:
            obj = self.tform.back
    else:
        obj = self.tform.edit_area
    t = obj.toPlainText()
    linktext = form.le_linktext.text()
    file_fi_used = form.le_fieldname.text()
    page_fi_used = form.le_page.text()
    functionname = f"open_in_external_helper_function__{uuid.uuid4().hex[:8]}"
    # t += (f"""<br><br><a href='javascript:pycmd("{sep_merge}{{{{text:{filefield}}}}}"""
    #       f"""{sep2}{{{{text:{pagefield}}}}}");'>{lt}</a>"""
    #       )
    """
    <br><br><a href='javascript:open_in_external_helper_function();'>View external file: {{text:external_source}}</a><script>function open_in_external_helper_function(){let mysource = String.raw`{{text:external_source}}`.replace(/\\/g, "\\\\");let mypage = "{{text:external_page}}";let mycmd = "open_external_files1994996371" + mysource +"1994996371" + mypage;pycmd(mycmd);}</script>
    """
    # lt = lt.replace("{","{{").replace("}","}}")

    t += f"""
<br><br>
<a href='javascript:{functionname}();'>{linktext}</a>
<script>
    function {functionname}(){{
        let mysource = String.raw`{{{{text:{file_fi_used}}}}}`.replace(/\\\\/g, "\\\\\\\\");
        let mypage = "{{{{text:{page_fi_used}}}}}";
        let mycmd = "{sep_merge}" + mysource + "{sep2}" + mypage;
        pycmd(mycmd);
    }}
</script>
"""
    obj.setPlainText(t)
    if pointversion < 28:
        self.saveCard()
CardLayout.onExtDocsLink = onExtDocsLink
