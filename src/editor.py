from anki.hooks import addHook
from anki.utils import (
    stripHTML,
)

from .config import gc
from .open_in_external import open_external


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
    a = menu.addAction("open file set in field %s" % gc("field_for_filename"))
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
