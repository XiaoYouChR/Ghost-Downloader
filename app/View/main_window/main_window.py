import os
from components.frameless_windows import AcrylicWindow
from View.settings_window import SettingsWindow
from components.system_tray_icon import SystemTrayIcon


class MainWindow(AcrylicWindow):
    """主窗口"""

    def __init__(self):
        super(MainWindow, self).__init__()
        # 简单初始化
        self.setObjectName("MainWindow")
        self.settingsWindow = SettingsWindow()
        if not os.path.exists("cache/"):
            os.mkdir("cache/")
        with open("cache/skinName", "w") as f:
            _ = self.settingsWindow.config.__getitem__("skin")
            f.write(_)

        self.systemTrayIcon = SystemTrayIcon(self)
        self.systemTrayIcon.show()
