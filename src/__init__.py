from pprint import pprint as pp

from aqt import mw
from aqt.clayout import CardLayout
from aqt.utils import tooltip, showInfo
from aqt.qt import *

from . import card_layout
from . import open_in_external
from . import my_config_window
from .forms import addtofield


def onMySettings():
    dialog = my_config_window.MyConfigWindow(mw.addonManager.getConfig(__name__))
    if dialog.exec_():
        mw.addonManager.writeConfig(__name__, dialog.config)
mw.addonManager.setConfigAction(__name__, onMySettings)
