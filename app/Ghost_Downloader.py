import ssl
import requests
import sys
from multiprocessing import freeze_support

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2.QtCore import Qt, QLockFile, QSize

from View.main_window import MainWindow
from common.get_skin_filename import getSkinFilename

if __name__ == '__main__':
    # 多进程需要
    freeze_support()

    # 忽略 https 警告
    ssl._create_default_https_context = ssl._create_unverified_context
    requests.packages.urllib3.disable_warnings()

    # 创建application
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    logoIcon = QIcon()
    logoIcon.addFile(logoIcon.addFile(getSkinFilename("Logo.png"), QSize(), QIcon.Normal, QIcon.Off))
    app.setWindowIcon(logoIcon)

    # 检测程序是否重复运行
    lockFile = QLockFile("./lock.lck")
    if not lockFile.tryLock(2000):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("提示")
        msgBox.setText("Ghost Downloader 2 已在运行!")
        msgBox.setIcon(QMessageBox.Information)
        msgBox.addButton("确定", QMessageBox.YesRole)
        msgBox.exec()
        sys.exit(-1)

    # 创建主窗口
    GhostDownloader = MainWindow()
    GhostDownloader.show()

    sys.exit(app.exec_())