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



This add-on uses the file fuzzy_panel.py which has this copyright and permission notice:

    Copyright (c): 2018  Rene Schallner
                   2019- ijgnd
        
    This file (fuzzy_panel.py) is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This file is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this file.  If not, see <http://www.gnu.org/licenses/>.



This add-on uses the file icons/folder-plus_mod.svg. This is a slight modification 
("black" instead of "currentColor") of the file 
https://raw.githubusercontent.com/feathericons/feather/master/icons/folder-plus.svg 
which is covered by the following copyright and permission notice,
https://github.com/feathericons/feather/blob/master/LICENSE:

    The MIT License (MIT)

    Copyright (c) 2013-2017 Cole Bemis

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

"""  


from pprint import pprint as pp

from aqt import mw
from aqt.clayout import CardLayout
from aqt.utils import tooltip, showInfo
from aqt.qt import *

from . import card_layout
from . import open_in_external
from . import config_window
from . import editor
from . import editor_insert_reference
from . import linked__view
from . import linked__editor
from . import reviewer

from .forms import addtofield


def onMySettings():
    dialog = config_window.AddonConfigWindow(mw.addonManager.getConfig(__name__))
    if dialog.exec_():
        mw.addonManager.writeConfig(__name__, dialog.config)
mw.addonManager.setConfigAction(__name__, onMySettings)
