import sys

from common.get_skin_filename import getSkinFilename
from PySide2.QtWidgets import QSystemTrayIcon, QAction, QApplication
from PySide2.QtGui import QIcon
from components.widgets.menus import DWMMenu


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super(SystemTrayIcon, self).__init__(parent)
        self.menu = SystemTrayMenu(parent)
        self.activated.connect(self.menu.showHome)
        self.setContextMenu(self.menu)
        self.setIcon(QIcon(getSkinFilename("Logo.png")))
        self.setToolTip("Ghost DownloadGroup -- 姚是晓游的！")

class SystemTrayMenu(DWMMenu):
    def __init__(self, parent=None):
        super(SystemTrayMenu, self).__init__(parent)

        self.setFixedWidth(175)

        self.showHomeAct = QAction(QIcon(getSkinFilename("Icon/主页.png")), "显示主界面", self)
        self.newTaskAct = QAction(QIcon(getSkinFilename("Icon/添加.png")), "新建下载任务", self)
        self.startAllAct = QAction(QIcon(getSkinFilename("Icon/播放.png")), "开始全部任务", self)
        self.pauseAllAct = QAction(QIcon(getSkinFilename("Icon/暂停.png")), "暂停全部任务", self)
        self.ExitAct = QAction(QIcon(getSkinFilename("Icon/启动.png")), "关闭软件", self)

        self.showHomeAct.triggered.connect(self.showHome)
        self.ExitAct.triggered.connect(lambda: sys.exit(0))

        self.addAction(self.showHomeAct)
        self.addSeparator()
        self.addActions([self.newTaskAct, self.startAllAct, self.pauseAllAct])
        self.addSeparator()
        self.addAction(self.ExitAct)

        self.setObjectName('systemTrayMenu')

        self.setStyle(QApplication.style())

    def showHome(self):
        self.parent().show()
        self.parent().raise_()
