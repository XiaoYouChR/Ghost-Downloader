import threading
import time
from webbrowser import open_new_tab

import requests
from PySide2.QtCore import QRect, QPropertyAnimation, QEasingCurve, QPoint
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QGroupBox, QLabel, QTextEdit, QWidget, QPushButton, QComboBox

from View.new_net_task_window import NewNetTaskWindow
from common.get_surf_info import headers, proxy
from components.widgets.dialog import Dialog


class ListGroupBox(QGroupBox):
    def __init__(self, parent, name: str, filesize, info: str, updata, version, uplog: str, filename, downurl, videourl,
                 icon):
        super().__init__(parent=parent)

        self.w = self.width()
        self.h = self.height()

        self.name = name
        self.filesize = filesize
        self.info = info
        self.updata = updata
        self.version = version
        self.uplog = uplog
        self.filename = filename
        self.downurl = downurl
        self.videourl = videourl
        self.icon = icon
        # 初始化展开状态
        self.opened = False
        # 初始化ComboBox选项
        self.currentIndex = 0

        self.setObjectName("ListGroupBox")
        # 临时
        self.setStyleSheet(u"QPushButton {"
                           "    border-radius: 0px;"
                           "    background: rgb(120, 170, 220);"
                           "    color: white;"
                           "}"
                           "QPushButton:!enabled {\n"
                           "        background: rgb(180, 180, 180);\n"
                           "        color: white;\n"
                           "}\n"
                           "QPushButton:enabled:hover{\n"
                           "        background: rgb(100, 160, 220);\n"
                           "}\n"
                           "QPushButton:enabled:pressed{\n"
                           "        background: rgb(0, 78, 161);\n"
                           "}"  
                           "QPushButton#downBtn {\n"
                           "        border-top-right-radius: 10px;\n"
                           "		border-bottom-right-radius: 10px;\n"
                           "        border: 1px solid rgb(0, 170, 255);\n"
                           "}\n"
                           "QPushButton#moreBtn {\n"
                           "        border-top-left-radius: 10px;\n"
                           "		border-bottom-left-radius: 10px;\n"
                           "        border: 1px solid rgb(0, 170, 255);\n"
                           "}\n"
                           "QPushButton[round=\"true\"] {\n"
                           "		border-radius: 10px;\n"
                           "        border: 1px solid rgb(0, 170, 255);\n"
                           "}\n"
                           "QComboBox {\n"
                           "        border-radius: 9px;\n"
                           "        border: 1px solid rgb(111, 156, 207);\n"
                           "        background: white;\n"
                           "}\n")

        # setUp
        self.imgLable = QLabel(self)
        self.imgLable.setScaledContents(True)
        self.imgLable.setGeometry(QRect(5, 16, 81, 81))

        self.infoEdit = QTextEdit(self)
        self.infoEdit.setGeometry(QRect(90, 20, 401, 71))
        self.infoEdit.setReadOnly(True)

        # More
        self.moreWidget = QWidget(self)
        self.moreWidget.setGeometry(505, 20, 61, 21)
        self.moreWidget.setObjectName("moreWidget")

        # 临时
        self.moreWidget.setStyleSheet(u".QWidget#moreWidget{\n"
                                      "	border:1px solid rgb(0, 170, 255);\n"
                                      "	background:white;\n"
                                      "	border-radius: 10px;\n"
                                      "}")
        # 临时

        self.upDataLabel = QLabel(self.moreWidget)
        self.upDataLabel.setGeometry(QRect(165, 0, 176, 21))

        self.fileSizeLabel = QLabel(self.moreWidget)
        self.fileSizeLabel.setGeometry(QRect(340, 0, 119, 20))

        self.label = QLabel(self.moreWidget)
        self.label.setGeometry(QRect(31, 1, 36, 19))
        # 功能性控件
        self.moreBtn = QPushButton(self.moreWidget)
        self.moreBtn.setObjectName("moreBtn")
        self.moreBtn.setGeometry(QRect(0, 0, 21, 21))

        self.verComboBox = QComboBox(self.moreWidget)
        self.verComboBox.setGeometry(QRect(70, 1, 90, 19))

        self.videoBtn = QPushButton(self)
        self.videoBtn.setProperty("round", True)
        self.videoBtn.setGeometry(QRect(505, 45, 61, 21))

        self.logsBtn = QPushButton(self)
        self.logsBtn.setProperty("round", True)
        self.logsBtn.setGeometry(QRect(505, 70, 61, 22))
        self.logsBtn.setEnabled(False)

        self.downBtn = QPushButton(self.moreWidget)
        self.downBtn.setObjectName("downBtn")
        self.downBtn.setGeometry(QRect(20, 0, 41, 21))
        self.downBtn.setEnabled(False)

        threading.Thread(target=self.setImg, daemon=True).start()  # 设置头图

        # Animation
        self.moreWidgetAnimation = QPropertyAnimation(self.moreWidget, b"geometry")
        self.moreWidgetAnimation.setDuration(500)
        self.moreWidgetAnimation.setEasingCurve(QEasingCurve.OutQuart)

        self.downBtnAnimation = QPropertyAnimation(self.downBtn, b"pos")
        self.downBtnAnimation.setDuration(500)
        self.downBtnAnimation.setEasingCurve(QEasingCurve.OutQuart)

        # 连接信号
        self.moreBtn.clicked.connect(self.Open)
        self.videoBtn.clicked.connect(lambda: open_new_tab(self.videourl[self.currentIndex]))
        self.verComboBox.currentIndexChanged.connect(self.changeVersion)
        self.logsBtn.clicked.connect(lambda: Dialog(self.parent().parent().parent().parent(), f"{self.name}の更新日志", self.uplog).exec_())
        self.downBtn.clicked.connect(
            lambda: NewNetTaskWindow(f"cache/{self.name}-icon", downurl[self.currentIndex], filename[self.currentIndex],
                                     parent.parent()))

        # setText
        self.setTitle(self.name)
        self.moreBtn.setText("◀")
        self.label.setText("版本:")
        self.verComboBox.addItems(self.version)
        self.downBtn.setText("下载")
        self.videoBtn.setText("视频")
        self.logsBtn.setText("日志")
        self.infoEdit.setText(self.info)

    def Open(self):
        if self.opened == False:  # 没有展开就展开
            self.moreWidgetAnimation.setEndValue(QRect(self.w - 500, 20, 491, 21))
            self.moreWidgetAnimation.start()
            self.downBtnAnimation.setEndValue(QPoint(450, 0))
            self.downBtnAnimation.start()
            self.moreBtn.setText("▶")
            self.opened = True

        elif self.opened == True:  # 展开了就收起
            self.moreWidgetAnimation.setEndValue(QRect(self.w - 70, 20, 61, 21))
            self.moreWidgetAnimation.start()
            self.downBtnAnimation.setEndValue(QPoint(20, 0))
            self.downBtnAnimation.start()
            self.moreBtn.setText("◀")
            self.opened = False

    def setImg(self):

        complete = False
        while not complete:
            try:
                self.icon = requests.get(url=self.icon, headers=headers, proxies=proxy).content
                complete = True
            except Exception:
                time.sleep(0.5)

        with open(f'cache/{self.name}-icon', 'wb') as f:
            f.write(self.icon)
            f.close()
        self.icon = QPixmap(f'cache/{self.name}-icon')
        self.imgLable.setPixmap(self.icon)
        self.logsBtn.setEnabled(True)
        self.downBtn.setEnabled(True)

    def changeVersion(self):
        self.currentIndex = self.verComboBox.currentIndex()
        self.fileSizeLabel.setText(f"大小:{self.filesize[self.currentIndex]}")
        self.upDataLabel.setText(f"更新日期:{self.updata[self.currentIndex]}")

    def resizeEvent(self, event):
        self.w = self.width()
        self.h = self.height()
        super().resizeEvent(event)
        self.infoEdit.resize(self.w - 175, 71)
        self.logsBtn.move(self.w - 70, 70)
        self.videoBtn.move(self.w - 70, 45)
        if self.opened == False:
            self.moreWidget.move(self.w - 70, 20)
        elif self.opened == True:
            self.moreWidget.move(self.w - 500, 20)
