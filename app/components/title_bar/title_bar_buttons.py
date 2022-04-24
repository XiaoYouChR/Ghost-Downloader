# coding:utf-8

from PySide2.QtCore import QSize, Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QToolButton

from common.get_skin_filename import getSkinFilename


class MaximizeButton(QToolButton):
    """ Maximize """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.iconPaths = [
            {'normal': getSkinFilename('TitleBar/Maximize_normal.png'),
             'hover': getSkinFilename('TitleBar/Maximize_hover.png'),
             'pressed': getSkinFilename('TitleBar/Maximize_press.png')},
            {'normal': getSkinFilename('TitleBar/Reduction_normal.png'),
             'hover': getSkinFilename('TitleBar/Reduction_hover.png'),
             'pressed': getSkinFilename('TitleBar/Reduction_press.png')}
        ]
        self.resize(15, 15)
        # 设置标志位
        self.isMax = False
        self.setIcon(
            QIcon(getSkinFilename('TitleBar/Maximize_normal.png')))
        self.setIconSize(QSize(15, 15))

    def __updateIcon(self, iconState: str):
        """ change the icon based on the iconState """
        self.setIcon(
            QIcon(self.iconPaths[self.isMax][iconState]))

    def enterEvent(self, e):
        self.__updateIcon('hover')

    def leaveEvent(self, e):
        self.__updateIcon('normal')

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            return
        self.__updateIcon('pressed')
        super().mousePressEvent(e)

    def setMaxState(self, isMax: bool):
        """ update the maximized state and icon """
        if self.isMax == isMax:
            return
        self.isMax = isMax
        self.__updateIcon('normal')


class ThreeStateToolButton(QToolButton):
    """ A ToolButton with different icons in normal, hover and pressed states """

    def __init__(self, iconPaths: dict, icon_size: tuple = (15, 15), parent=None):
        super().__init__(parent)
        self.iconPaths = iconPaths
        self.resize(*icon_size)
        self.setCursor(Qt.ArrowCursor)
        self.setIconSize(self.size())
        self.setIcon(QIcon(self.iconPaths['normal']))
        self.setStyleSheet('border: none; margin: 0px')

    def enterEvent(self, e):
        """ hover时更换图标 """
        self.setIcon(QIcon(self.iconPaths['hover']))

    def leaveEvent(self, e):
        """ leave时更换图标 """
        self.setIcon(QIcon(self.iconPaths['normal']))

    def mousePressEvent(self, e):
        """ 鼠标左键按下时更换图标 """
        if e.button() == Qt.RightButton:
            return
        self.setIcon(QIcon(self.iconPaths['pressed']))
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        """ 鼠标左键按下时更换图标 """
        if e.button() == Qt.RightButton:
            return
        self.setIcon(QIcon(self.iconPaths['normal']))
        super().mouseReleaseEvent(e)
