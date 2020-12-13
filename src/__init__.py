"""
Add-on for Anki 2.1: Open linked pdf, docs, epub, audio, video, etc in external Program

Copyright: (c) 2019- ijgnd
               2020 Y. H. Lai (yhlai-code) osascript-helper function, 
                       see https://github.com/ijgnd/anki21__OpenInExternalEditor_Rename_Duplicate_for_Image_Audio_Video/pull/2


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

from pprint import pprint as pp

from aqt import mw
from aqt.clayout import CardLayout
from aqt.utils import tooltip, showInfo
from aqt.qt import *

from . import card_layout
from . import open_in_external
from . import my_config_window

from . import linked__view
from . import linked__editor

from .forms import addtofield


def onMySettings():
    dialog = my_config_window.MyConfigWindow(mw.addonManager.getConfig(__name__))
    if dialog.exec_():
        mw.addonManager.writeConfig(__name__, dialog.config)
mw.addonManager.setConfigAction(__name__, onMySettings)
