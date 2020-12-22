from anki.hooks import wrap

from aqt.reviewer import Reviewer
from .consts import sep2, sep_merge
from .open_in_external import open_external


def myLinkHandler(self, url, _old):
    if url.startswith(sep_merge):
        file, page = url.replace(sep_merge, "").split(sep2)
        open_external(file, page)
    else:
        return _old(self, url)
Reviewer._linkHandler = wrap(Reviewer._linkHandler, myLinkHandler, "around")
