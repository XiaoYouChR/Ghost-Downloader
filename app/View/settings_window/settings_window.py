from components.frameless_windows import AcrylicWindow

from .config import Config


class SettingsWindow(AcrylicWindow):
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__(parent)

        self.setObjectName("SettingsWindow")


config = Config()
