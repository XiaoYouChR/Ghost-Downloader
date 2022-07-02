import os
import threading
from re import findall

import requests
from PySide2.QtCore import QSize, QPropertyAnimation, QEasingCurve, QRect, Signal, Qt
from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtWidgets import QPushButton, QLabel, QWidget, QScrollArea

from View.settings_window import SettingsWindow
from common.get_global_info import proxy, headers
from common.get_skin_filename import getSkinFilename
from components.frameless_windows import AcrylicWindow
from components.system_tray_icon import SystemTrayIcon
from components.widgets.groups import ListGroupBox
from components.widgets.labels import PictureLabel
from components.widgets.progress_bar import MyProgressBar
from components.widgets.dialog import Dialog
from .down_widget import DownWidget
from ..settings_window.settings_window import config

print(proxy, headers)

# Define Global Value
listGroupBoxesList = []

class MainWindow(AcrylicWindow):
    """主窗口"""
    load_list = Signal(str)  # 加载列表的信号
    opened = False  # 系统列表展开状态
    listNotLoaded = True  # 系统列表加载状态

    def __init__(self):
        super(MainWindow, self).__init__()
        # 简单初始化
        self.setObjectName("MainWindow")

        self.settingsWindow = SettingsWindow()

        if not os.path.exists("cache/"):
            os.mkdir("cache/")
        with open("cache/skinName", "w") as f:
            _ = config.__getitem__("skin")
            f.write(_)

        with open(getSkinFilename("QSS/main_window.qss"), "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())
            f.close()

        self.systemTrayIcon = SystemTrayIcon(self)
        self.systemTrayIcon.show()

        self.setFixedSize(600, 600)

        self.setUp()

    def setUp(self):
        self.logoPixmap = QPixmap(getSkinFilename("Logo.png"))
        self.logoLabel = PictureLabel(self, self.logoPixmap)
        self.logoLabel.setGeometry(22, 22, 26, 26)

        self.addTaskBtn = QPushButton(self)
        self.addTaskBtn.setObjectName("addTaskBtn")
        # self.addTaskBtn.setProperty("round", True)
        self.addTaskBtn.setGeometry(278, 12, 45, 45)
        self.addTaskBtn.setIcon(QIcon(getSkinFilename("Icon/AddTaskBtn.png")))
        self.addTaskBtn.setToolTip("添加任务")
        self.addTaskBtn.setIconSize(QSize(45, 45))

        self.allTaskProgressBar = MyProgressBar(self)
        self.allTaskProgressBar.setObjectName("allTaskProgressBar")
        self.allTaskProgressBar.setGeometry(0, 68, 600, 3)

        self.downWidget = DownWidget(self)
        self.downWidget.setObjectName("downWidget")
        self.downWidget.setGeometry(0, 70, 600, 470)
        self.downWidget.setStyleSheet("""   QFrame#downWidget {border: 1px solid rgb(230, 230, 230)\n;
                                                               background:rgb(255, 255, 255);\n
                                                               }""")

        self.noTaskPixmap = QPixmap(getSkinFilename("Icon/暂无任务.png"))
        self.noTaskLabel = PictureLabel(self.downWidget, self.noTaskPixmap)
        self.noTaskLabel.setObjectName("noTaskLabel")
        self.noTaskLabel.setGeometry(225, 125, 150, 150)

        self.noTaskTextLabel = QLabel(self.downWidget)
        self.noTaskTextLabel.setText("noTaskTextLabel")
        self.noTaskTextLabel.setText("还没有下载任务哦！")
        self.noTaskTextLabel.move(235, 275)

        self.versionLabel = QLabel(self.titleBar)
        self.versionLabel.setGeometry(560,55,40,10)
        self.versionLabel.setText("0.9.9α")
        self.versionLabel.setStyleSheet("font:10px; color:rgb(50,50,50);")

        self.systemListWidget = QWidget()
        self.systemListWidget.setObjectName("systemListWidget")
        self.systemListWidget.resize(545, 530)
        self.systemListWidget.setStyleSheet(self.styleSheet())

        self.systemListScrollArea = QScrollArea(self)
        self.systemListScrollArea.setObjectName("systemListScrollArea")
        self.systemListScrollArea.setGeometry(475, 555, 100, 25)
        self.systemListScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.systemListScrollArea.setWidget(self.systemListWidget)

        # 系统列表Widgetのanimation
        self.systemListAnimation = QPropertyAnimation(self.systemListScrollArea, b"geometry")
        self.systemListAnimation.setDuration(750)
        self.systemListAnimation.setEasingCurve(QEasingCurve.OutQuart)

        self.openedBtn = QPushButton(self)
        self.openedBtn.setObjectName("openedBtn")
        self.openedBtn.setGeometry(475, 555, 100, 25)
        self.openedBtn.setText("打开系统列表")

        # Connect Signal to 槽
        self.openedBtn.clicked.connect(self.OpenedSystemList)
        self.load_list.connect(self.loadList)

    def loadList(self, content: str):
        global listGroupBoxesList

        content = findall(r"<tab>([\s\S]*?)</tab>", content)
        # 初始化
        self.len = len(content)
        listGroupBoxesList = []

        # 设置systemListWidget大小
        self.systemListWidget.resize(545, self.len * 105 + 5)

        for i in range(self.len):
            temp = content[i]

            name = findall(r'<name>([\s\S]*)</name>', temp)
            name = name[0]

            filesize = findall(r'<filesize>([\s\S]*)</filesize>', temp)
            filesize = filesize[0]
            filesize = findall(r'\|?([\s\S]*?)\|', filesize)

            info = findall(r'<info>([\s\S]*)</info>', temp)
            info = info[0]
            info = info.replace(r"\n", "\n")

            updata = findall(r'<updata>([\s\S]*)</updata>', temp)
            updata = updata[0]
            updata = findall(r'\|?([\s\S]*?)\|', updata)

            version = findall(r'<version>([\s\S]*)</version>', temp)
            version = version[0]
            version = findall(r'\|?([\s\S]*?)\|', version)

            uplog = findall(r'<uplog>([\s\S]*)</uplog>', temp)
            uplog = uplog[0]
            uplog = uplog.replace(r"\n", "\n")

            filename = findall(r'<filename>([\s\S]*)</filename>', temp)
            filename = filename[0]
            filename = findall(r'\|?([\s\S]*?)\|', filename)

            downurl = findall(r'<downurl>([\s\S]*)</downurl>', temp)
            downurl = downurl[0]
            downurl = findall(r'\|?([\s\S]*?)\|', downurl)

            videourl = findall(r'<videourl>([\s\S]*)</videourl>', temp)
            videourl = videourl[0]
            videourl = findall(r'\|?([\s\S]*?)\|', videourl)

            icon = findall(r'<icon>([\s\S]*)</icon>', temp)
            icon = icon[0]

            listGroupBoxesList.append(ListGroupBox(self.systemListWidget, name, filesize, info, updata, version, uplog, filename,
                                                 downurl, videourl, icon))

            listGroupBoxesList[i].resize(self.systemListWidget.width() - 20, 100)

            # Action
            listGroupBoxesList[i].move(0, i * 105 + 5)
            # moveAction(listGroupBoxesList[i], 5, i * 105 + 5)

            listGroupBoxesList[i].show()

        # self.loadingGifLable.close()

    def OpenedSystemList(self):

        if self.opened == False:  # 展开
            # print("展开", self.opened)
            self.opened = True
            self.openedBtn.setText("收起系统列表")
            self.systemListAnimation.stop()
            self.systemListAnimation.setEndValue(QRect(25, 25, 550, 555))
            self.systemListAnimation.start()

        elif self.opened == True:  # 收起
            # print("收起", self.opened)
            self.opened = False
            self.openedBtn.setText("打开系统列表")
            self.systemListAnimation.stop()
            self.systemListAnimation.setEndValue(QRect(475, 555, 100, 25))
            self.systemListAnimation.start()

        if self.listNotLoaded == True:  # 没加载就加载

            def getWebsiteContent():
                try:
                    content = requests.get("https://obs.cstcloud.cn/share/obs/xiaoyouchr/config.json", headers=headers,
                                           proxies=proxy, verify=False)
                    content.encoding = "utf-8"
                    content = content.text
                    self.load_list.emit(content)
                    self.listNotLoaded = False
                except requests.exceptions.ConnectionError as err:
                    print(err)
                    Dialog(self, "网络连接失败！", f"请尝试关闭代理！\n{err}").exec_()
                    self.listNotLoaded = True
                except ValueError as err:
                    print(err)
                    Dialog(self, "网络连接失败！", f"请检查网络连接！\n{err}").exec_()
                    self.listNotLoaded = True
                except Exception as err:
                    print(err)
                    Dialog(self, "未知错误!", f"请联系开发者,QQ:2078107317！\n{err}").exec_()
                    self.listNotLoaded = True

            threading.Thread(target=getWebsiteContent, daemon=True).start()

    def closeEvent(self, e):

        dialog = Dialog(self, "你在尝试退出哦!~", "你确定要退出 Ghost Downloader 吗?")
        dialog.yesSignal.connect(lambda: super(MainWindow, self).closeEvent(e))
        dialog.cancelSignal.connect(e.ignore)
        dialog.exec_()
