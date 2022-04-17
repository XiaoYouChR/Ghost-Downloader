# coding:utf-8

from PySide2.QtCore import Qt
from PySide2.QtGui import QResizeEvent
from PySide2.QtWidgets import QWidget
from win32.lib import win32con
from win32.win32api import SendMessage
from win32.win32gui import ReleaseCapture

from common.get_skin_filename import getSkinFilename

from .title_bar_buttons import MaximizeButton, ThreeStateToolButton


class TitleBar(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.minBtn = ThreeStateToolButton(
            {'normal': getSkinFilename('TitleBar/Minimize_normal.png'),
             'hover': getSkinFilename('TitleBar/Minimize_hover.png'),
             'pressed': getSkinFilename('TitleBar/Minimize_pressed.png')}, parent=self)
        self.closeBtn = ThreeStateToolButton(
            {'normal': getSkinFilename('TitleBar/Close_Normal.png'),
             'hover': getSkinFilename('TitleBar/Close_Hover.png'),
             'pressed': getSkinFilename('TitleBar/Close_Press.png')}, parent=self)
        self.maxBtn = MaximizeButton(self)
        self.__initWidget()

    def __initWidget(self):
        """ initialize all widgets """
        self.resize(1360, 40)
        self.setFixedHeight(40)
        self.setAttribute(Qt.WA_StyledBackground)
        self.__setQss()

        # connect signal to slot
        self.minBtn.clicked.connect(self.window().showMinimized)
        self.maxBtn.clicked.connect(self.__toggleMaxState)
        self.closeBtn.clicked.connect(self.window().close)

    def resizeEvent(self, e: QResizeEvent):
        """ Move the buttons """
        self.closeBtn.move(self.width() - 20, 5)
        self.maxBtn.move(self.width() - 2 * 20, 5)
        self.minBtn.move(self.width() - 3 * 20, 5)

    def mouseDoubleClickEvent(self, event):
        """ Toggles the maximization state of the window """
        self.__toggleMaxState()

    def mousePressEvent(self, event):
        """ Move the window """
        if not self.__isPointInDragRegion(event.pos()):
            return

        ReleaseCapture()
        SendMessage(self.window().winId(), win32con.WM_SYSCOMMAND,
                    win32con.SC_MOVE + win32con.HTCAPTION, 0)
        event.ignore()

    def __toggleMaxState(self):
        """ Toggles the maximization state of the window and change icon """
        if self.window().isMaximized():
            self.window().showNormal()
            # change the icon of maxBtn
            self.maxBtn.setMaxState(False)
        else:
            self.window().showMaximized()
            self.maxBtn.setMaxState(True)

    def __isPointInDragRegion(self, pos) -> bool:
        """ Check whether the pressed point belongs to the area where dragging is allowed """
        right = self.width() - 20 * 3 if self.minBtn.isVisible() else self.width() - 20
        return 0 < pos.x() < right

    def __setQss(self):
        self.setStyleSheet("QWidget {\n"
                           "            background-color: transparent\n"
                           "            }\n"
                           "            \n"
                           "            QToolButton{\n"
                           "            background-color: transparent;\n"
                           "            border: none;\n"
                           "            margin: 0px;\n"
                           "            }")
