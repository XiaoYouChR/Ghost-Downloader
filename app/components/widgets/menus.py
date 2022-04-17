from common.window_effect import WindowEffect
from PySide2.QtCore import QEvent, QFile, Qt
from PySide2.QtWidgets import QMenu
from common.get_skin_filename import getSkinFilename

class AeroMenu(QMenu):
    """ Aero menu """

    def __init__(self, string="", parent=None):
        super().__init__(string, parent)
        self.windowEffect = WindowEffect()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground | Qt.WA_StyledBackground)
        self.setObjectName("AeroMenu")
        self.setQss()

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            self.setMenuEffect()
        return QMenu.event(self, e)

    def setMenuEffect(self):
        """ set menu effect """
        self.windowEffect.setAeroEffect(self.winId())
        self.windowEffect.addMenuShadowEffect(self.winId())

    def setQss(self):
        """ set style sheet """
        f = QFile(getSkinFilename('QSS/menu.qss'))
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()


class AcrylicMenu(QMenu):
    """ Acrylic menu """

    def __init__(self, string="", parent=None, acrylicColor="e5e5e5CC"):
        super().__init__(string, parent)
        self.acrylicColor = acrylicColor
        self.windowEffect = WindowEffect()
        self.__initWidget()

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            self.windowEffect.setAcrylicEffect(
                self.winId(), self.acrylicColor, True)
        return QMenu.event(self, e)

    def __initWidget(self):
        """ initialize widgets """
        self.setAttribute(Qt.WA_StyledBackground)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setProperty("effect", "acrylic")
        self.setObjectName("acrylicMenu")
        self.setQss()

    def setQss(self):
        """ set style sheet """
        f = QFile(getSkinFilename('QSS/menu.qss'))
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()


class DWMMenu(QMenu):
    """ A menu with DWM shadow """

    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.windowEffect = WindowEffect()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setQss()

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            self.windowEffect.addMenuShadowEffect(self.winId())
        return QMenu.event(self, e)

    def setQss(self):
        """ set style sheet """
        f = QFile(getSkinFilename('QSS/menu.qss'))
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()