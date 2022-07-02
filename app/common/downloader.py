from os import path
from xml.dom.minidom import parse, Document

from PySide2.QtGui import QPixmap

from common.get_global_info import DownGroupBoxesList
from components.widgets.dialog import Dialog


class Downloader:
    def __init__(self, iconPath: str, url: str, filename: str, download_dir: str, block_num: int, parent=None,
                 autoStarted=False):

        self.iconPath = iconPath
        self.url = url
        self.filename = filename
        self.download_dir = download_dir
        self.block_num = block_num
        self.parent = parent

        if path.exists("history.xml"):  # 文件存在就读取

            self.domTree = parse("./history.xml")
            self.rootNode = self.domTree.documentElement

            print(self.rootNode.nodeName)

            tasks = self.rootNode.getElementsByTagName("task")

            for task in tasks:  # 检测是不是有BUG
                __filename = task.getElementsByTagName("filename")[0]
                print("filename:", __filename)
                __download_dir = task.getElementsByTagName("download_dir")[0]
                print("download_dir", __download_dir)
                __url = task.getElementsByTagName("url")[0]
                print("url:", __url)
                if __download_dir == download_dir and __filename == filename:
                    print("当前目录下有同名文件！请更改文件名或路径后重试！")
                    return

                if __url == url:
                    print("重复下载同一文件！")
                    return

            if not autoStarted:
                # 写入历史
                self.whiteHistory()

        else:
            # 没有文件自己造
            self.domTree = Document()
            self.rootNode = self.domTree.createElement("tasks")
            self.domTree.appendChild(self.rootNode)
            self.whiteHistory()

        # icon = QPixmap(iconPath)

    def whiteHistory(self):
        taskNode = self.domTree.createElement("task")

        filenameNode = self.domTree.createElement("filename")
        filenameTextValue = self.domTree.createTextNode(self.filename)
        filenameNode.appendChild(filenameTextValue)
        taskNode.appendChild(filenameNode)

        download_dirNode = self.domTree.createElement("download_dir")
        download_dirTextValue = self.domTree.createTextNode(self.download_dir)
        download_dirNode.appendChild(download_dirTextValue)
        taskNode.appendChild(download_dirNode)

        urlNode = self.domTree.createElement("url")
        urlTextValue = self.domTree.createTextNode(self.url)
        urlNode.appendChild(urlTextValue)
        taskNode.appendChild(urlNode)

        block_numNode = self.domTree.createElement("block_num")
        block_numTextValue = self.domTree.createTextNode(str(self.block_num))
        block_numNode.appendChild(block_numTextValue)
        taskNode.appendChild(block_numNode)

        iconNode = self.domTree.createElement("icon")
        iconTextValue = self.domTree.createTextNode(self.iconPath)
        iconNode.appendChild(iconTextValue)
        taskNode.appendChild(iconNode)

        self.rootNode.appendChild(taskNode)

        with open("./history.xml", "w") as f:
            # 缩进 - 换行 - 编码
            self.domTree.writexml(f, addindent='    ', newl='\n', encoding='GBK')
            f.close()
