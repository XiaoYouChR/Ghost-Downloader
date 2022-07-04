from re import IGNORECASE, findall, compile

import requests
from PySide2.QtCore import QSize
from PySide2.QtWidgets import QDialog, QVBoxLayout, QGroupBox, QHBoxLayout, QLabel, QComboBox, QRadioButton, \
    QSizePolicy, QPushButton, QLineEdit

from View.settings_window.settings_window import config
from Download_Engine import DownloadGroup
from common.get_skin_filename import getSkinFilename
from common.get_global_info import headers, proxy
from common.tools import decidePathWin
from components.widgets.dialog import Dialog


class NewNetTaskWindow(QDialog):
    def __init__(self, icon, downurl, filename, parent=None):
        super().__init__(parent)

        self.icon = icon
        self.mainWindow = self.parent().parent().parent()

        print(self.mainWindow)

        self.threadNum = config.__getitem__("block-num")

        # QSS
        with open(getSkinFilename("QSS/main_window.qss"), "r", encoding="utf-8") as f:
            _ = f.read()
            self.setStyleSheet(_)
            f.close()

        print(f"{icon}\n{downurl}\n{filename}")

        self.setUp()
        # 自定义功能区
        WPSsupport = compile(u"\^\^\^\^\^", IGNORECASE).search(downurl)
        WPSSupport_2 = compile(u"\^\^\^\^\^\$\$\$\$\$", IGNORECASE).search(downurl)
        CSTsupport = compile(u"\$\$\$\$\$", IGNORECASE).search(downurl)
        print(WPSSupport_2)

        print("OD支持")
        self.WPSRadioBtn.setDisabled(True)
        self.CSTRadioBtn.setDisabled(True)
        self.ODurl = downurl
        self.ODname = filename
        self.ODRadioBtn.setChecked(True)  # 默认Onedrive

        if CSTsupport:
            print("CST支持")
            self.CSTRadioBtn.setDisabled(False)
            self.ODurl = findall(u"([\S\s]*)\^\^\^\^\^", downurl)[0]
            self.CSTurl = findall(u"\$\$\$\$\$([\S\s]*)", downurl)[0]
            self.ODname = findall(u"([\S\s]*)\^\^\^\^\^", filename)[0]
            self.CSTname = findall(u"\$\$\$\$\$([\S\s]*)", filename)[0]
        if WPSsupport and not WPSSupport_2:
            print("WPS支持")
            self.WPSRadioBtn.setDisabled(False)
            self.WPSurl = findall(u"\^\^\^\^\^([\S\s]*)\$\$\$\$\$", downurl)[0]
            self.WPSurl = findall(u",?([\S\s]*?),", self.WPSurl)
            print(self.WPSurl)
            self.WPSname = findall(u"\^\^\^\^\^([\S\s]*)\$\$\$\$\$", filename)[0]
            self.WPSname = findall(u",?([\S\s]*?),", self.WPSname)
            print(self.WPSname)
            self.WPSRadioBtn.setChecked(True)  # 默认WPS

        # 连接函数
        self.threadNumC.currentIndexChanged.connect(self.changeThreadNum)
        self.decidePathBtn.clicked.connect(lambda: decidePathWin(self.mainWindow, self.decidePathEdit, False))
        self.startBtn.clicked.connect(self.startDownload)
        # 保持运行
        self.exec_()

    def changeThreadNum(self):
        temp = self.threadNum
        self.threadNum = int(self.threadNumC.currentText())
        print(self.threadNum)
        if temp >= 32:
            if self.threadNum < 32:
                warning = Dialog(self.mainWindow, '警告！', '你选择的线程过低！很可能会造成下载速度过慢或其他BUG！\n\n你确定要选择小于32个下载线程吗？')

                def cancel():
                    self.threadNum = temp
                    self.threadNumC.setCurrentIndex(self.threadNum - 1)

                warning.cancelSignal.connect(cancel)

                warning.exec_()

            elif temp <= 256:
                if self.threadNum > 256:
                    warning = Dialog(self.mainWindow, '警告！', '你选择的线程过高！可能把您的电脑淦爆！\n\n你确定要选择大于256个下载线程吗？')

                    def cancel():
                        self.threadNum = temp
                        self.threadNumC.setCurrentIndex(self.threadNum - 1)

                    warning.cancelSignal.connect(cancel)

                    warning.exec_()


    def setUp(self):
        self.setObjectName(u"NewNetTaskWindow")
        self.resize(500, 220)
        self.setMinimumSize(QSize(500, 250))
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.threadNumG = QGroupBox(self)
        self.threadNumG.setObjectName(u"threadNumG")
        self.horizontalLayout_2 = QHBoxLayout(self.threadNumG)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.warningLabel = QLabel(self.threadNumG)
        self.warningLabel.setObjectName(u"warningLabel")

        self.horizontalLayout_2.addWidget(self.warningLabel)

        self.threadNumC = QComboBox(self.threadNumG)
        self.threadNumC.setObjectName(u"threadNumC")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.threadNumC.sizePolicy().hasHeightForWidth())
        self.threadNumC.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.threadNumC)

        self.verticalLayout.addWidget(self.threadNumG)

        self.decidePathG = QGroupBox(self)
        self.decidePathG.setObjectName(u"decidePathG")
        self.horizontalLayout = QHBoxLayout(self.decidePathG)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.decidePathEdit = QLineEdit(self.decidePathG)
        self.decidePathEdit.setObjectName(u"decidePathEdit")
        self.decidePathEdit.setReadOnly(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.decidePathEdit.sizePolicy().hasHeightForWidth())
        self.decidePathEdit.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.decidePathEdit)

        self.decidePathBtn = QPushButton(self.decidePathG)
        self.decidePathBtn.setObjectName(u"decidePathBtn")
        self.decidePathBtn.setProperty("round", True)
        sizePolicy2 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Ignored)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.decidePathBtn.sizePolicy().hasHeightForWidth())
        self.decidePathBtn.setSizePolicy(sizePolicy2)

        self.horizontalLayout.addWidget(self.decidePathBtn)

        self.verticalLayout.addWidget(self.decidePathG)

        self.decideSourceG = QGroupBox(self)
        self.decideSourceG.setObjectName(u"decideSourceG")
        self.horizontalLayout_3 = QHBoxLayout(self.decideSourceG)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.WPSRadioBtn = QRadioButton(self.decideSourceG)
        self.WPSRadioBtn.setObjectName(u"WPSRadioBtn")
        sizePolicy2.setHeightForWidth(self.WPSRadioBtn.sizePolicy().hasHeightForWidth())
        self.WPSRadioBtn.setSizePolicy(sizePolicy2)

        self.horizontalLayout_3.addWidget(self.WPSRadioBtn)

        self.ODRadioBtn = QRadioButton(self.decideSourceG)
        self.ODRadioBtn.setObjectName(u"ODRadioBtn")
        sizePolicy2.setHeightForWidth(self.ODRadioBtn.sizePolicy().hasHeightForWidth())
        self.ODRadioBtn.setSizePolicy(sizePolicy2)

        self.horizontalLayout_3.addWidget(self.ODRadioBtn)

        self.CSTRadioBtn = QRadioButton(self.decideSourceG)
        self.CSTRadioBtn.setObjectName(u"CSTRadioBtn")
        sizePolicy2.setHeightForWidth(self.CSTRadioBtn.sizePolicy().hasHeightForWidth())
        self.CSTRadioBtn.setSizePolicy(sizePolicy2)

        self.horizontalLayout_3.addWidget(self.CSTRadioBtn)

        self.ODRadioBtn.raise_()
        self.WPSRadioBtn.raise_()
        self.CSTRadioBtn.raise_()

        self.verticalLayout.addWidget(self.decideSourceG)

        self.startBtn = QPushButton(self)
        self.startBtn.setObjectName(u"startBtn")
        self.startBtn.setProperty("round", True)
        sizePolicy3 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.startBtn.sizePolicy().hasHeightForWidth())
        self.startBtn.setSizePolicy(sizePolicy3)

        self.verticalLayout.addWidget(self.startBtn)

        # 设置文本
        self.setWindowTitle(u"\u65b0\u5efa\u4e0b\u8f7d\u4efb\u52a1")
        self.threadNumG.setTitle(u"\u786e\u5b9a\u60a8\u7684\u4e0b\u8f7d\u7ebf\u7a0b\u6570")
        self.threadNumC.addItems([str(i + 1) for i in range(2048)])
        self.threadNumC.setCurrentIndex(self.threadNum - 1)
        self.warningLabel.setText(
            u"\u8bf7\u52ff\u8bbe\u7f6e\u8fc7\u9ad8\u7684\u4e0b\u8f7d\u7ebf\u7a0b,\u56e0\u4e3a\u8fd9\u53ef\u80fd\u9020\u6210\u7535\u8111\u5361\u987f\u548c\u4e0b\u8f7d\u5931\u8d25!")
        self.decidePathG.setTitle(u"\u786e\u5b9a\u60a8\u7684\u4e0b\u8f7d\u8def\u5f84")
        self.decidePathEdit.setText(config.__getitem__("download-folder"))
        self.decidePathBtn.setText(u"\u9009\u62e9\u8def\u5f84")
        self.decideSourceG.setTitle(u"\u9009\u62e9\u60a8\u7684\u4e0b\u8f7d\u6e90!")
        self.WPSRadioBtn.setText(u"金山云(移动电信)")
        self.ODRadioBtn.setText(u"微软云(联通电信)")
        self.CSTRadioBtn.setText(u"科技网(三网优化)")
        self.startBtn.setText(u"\u5f00\u59cb\u4e0b\u8f7d")

    def getWPSDownloadLink(self):
        DownloadLink = []  # 生成空列表
        session = requests.Session()
        session.headers.update(headers)
        session.proxies.update(proxy)
        for i in self.WPSurl:
            # session.get("https://www.kdocs.cn/view/l/ssazQO5dfN4s")
            response = session.get(url=i, allow_redirects=False).text
            URL = findall(r"\"url\":\"([\S\s]*)\",\"sha1", response)
            URL = URL[0].encode("utf-8").decode("unicode_escape")
            print(URL)
            DownloadLink.append(URL)
        return DownloadLink

    def startDownload(self):
        print(self.threadNum)

        print(self.decidePathEdit.text())

        if self.WPSRadioBtn.isChecked() == True:  # WPS
            DownloadLink = self.getWPSDownloadLink()
            for i in range(len(DownloadLink)):
                DownloadGroup(self.icon, DownloadLink[i], self.WPSname[i], self.decidePathEdit.text(), self.threadNum,
                              self.mainWindow.downWidget)
        elif self.ODRadioBtn.isChecked() == True:  # OD
            DownloadGroup(self.icon, self.ODurl, self.ODname, self.decidePathEdit.text(), self.threadNum, self.mainWindow.downWidget)
        elif self.CSTRadioBtn.isChecked() == True:  # CST
            DownloadGroup(self.icon, self.CSTurl, self.CSTname, self.decidePathEdit.text(), self.threadNum, self.mainWindow.downWidget)

        self.close()
