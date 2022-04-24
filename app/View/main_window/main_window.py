import os

from PySide2.QtCore import QSize
from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtWidgets import QPushButton

from View.settings_window import SettingsWindow
from common.get_skin_filename import getSkinFilename
from components.frameless_windows import AcrylicWindow
from components.system_tray_icon import SystemTrayIcon
from components.widgets.labels import PictureLabel
from .down_widget import DownWidget


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

        with open(getSkinFilename("QSS/main_window.qss"),"r",encoding="utf-8") as f:
            self.setStyleSheet(f.read())
            f.close()

        self.systemTrayIcon = SystemTrayIcon(self)
        self.systemTrayIcon.show()

        self.resize(600,600)

        self.setUp()

    def setUp(self):
        self.logoPixmap = QPixmap(getSkinFilename("Logo.png"))
        self.logoLabel = PictureLabel(self,self.logoPixmap)
        self.logoLabel.setGeometry(22, 22, 26, 26)

        self.addTaskBtn = QPushButton(self)
        self.addTaskBtn.setObjectName("addTaskBtn")
        self.addTaskBtn.setProperty("round", True)
        self.addTaskBtn.setGeometry(278,12,45,45)
        self.addTaskBtn.setIcon(QIcon(getSkinFilename("Icon/AddTaskBtn.png")))
        self.addTaskBtn.setIconSize(QSize(45,45))

        self.downWidget = DownWidget(self)
        self.downWidget.setGeometry(0,70,600,470)
        self.downWidget.setStyleSheet("""	border-radius: 10px;\n
                                            border: 3px solid rgb(0, 170, 255);""")
