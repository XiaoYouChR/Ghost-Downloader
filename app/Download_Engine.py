import glob
import os
import ssl
import sys
import threading
import time
from datetime import timedelta
from multiprocessing import Process
from os import path, startfile
from xml.dom.minidom import parse, Document

import requests
from PySide2.QtCore import QRect, QSize, Qt, Signal, QObject, QPropertyAnimation, QEasingCurve
from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtWidgets import QGroupBox, QLabel, QPushButton

from common.get_global_info import DownGroupBoxesList, proxy
from common.get_skin_filename import getSkinFilename
from components.widgets.dialog import Dialog
from components.widgets.labels import PictureLabel
from components.widgets.progress_bar import MyProgressBar

# 忽略 https 警告
ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings()

class DLWorker:  # 线程
    def __init__(self, name: str, url: str, range_start, range_end, cache_dir, finish_callback, user_agent):
        self.name = name
        self.url = url
        self.cache_filename = path.join(cache_dir, name + ".d2l")
        self.range_start = range_start  # 固定不动
        self.range_end = range_end  # 固定不动
        self.range_curser = range_start  # curser 所指尚未开始
        self.finish_callback = finish_callback  # 通知调用 DLWorker 的地方
        self.terminate_flag = False  # 该标志用于终结自己
        self.FINISH_TYPE = ""  # DONE 完成工作, HELP 需要帮忙, RETIRE 不干了
        self.user_agent = user_agent

    def __run(self):
        chunk_size = 1 * 1024  # 1 kb
        headers = {
            'User-Agent': self.user_agent,
            'Range': f'Bytes={self.range_curser}-{self.range_end}',
            'Accept-Encoding': '*'
        }
        req = requests.get(self.url, stream=True, verify=False, headers=headers, proxies=proxy)
        ####################################
        # Informational responses (100–199)
        # Successful responses (200–299)
        # Redirection messages (300–399)
        # Client error responses (400–499)
        # Server error responses (500–599)
        ####################################
        if 200 <= req.status_code <= 299:
            with open(self.cache_filename, "wb") as cache:
                try:
                    for chunk in req.iter_content(chunk_size=chunk_size):
                        if self.terminate_flag:
                            break
                        cache.write(chunk)
                        self.range_curser += len(chunk)
                except Exception as err:  # 错误之后发送信号自动重试
                    self.FINISH_TYPE = "ERROR"
                    self.terminate_flag = False
                    print(err)  # Debug

        if not self.terminate_flag:  # 只有正常退出才能标记 DONE，但是三条途径都经过此处
            self.FINISH_TYPE = "DONE"
        req.close()
        self.finish_callback(self)  # 执行回调函数，根据 FINISH_TYPE 结局不同

    def start(self):
        threading.Thread(target=self.__run).start()

    def help(self):
        self.FINISH_TYPE = "HELP"
        self.terminate_flag = True

    def retire(self):
        self.FINISH_TYPE = "RETIRE"
        self.terminate_flag = True

    def __lt__(self, another):
        """用于排序"""
        return self.range_start < another.range_start

    def get_progress(self):
        """获得进度"""
        _progress = {
            "curser": self.range_curser,
            "start": self.range_start,
            "end": self.range_end
        }
        return _progress


class DownloadGroup(QGroupBox):
    setTextSignal = Signal(QObject, str)

    def __init__(self, iconPath: str, url: str, filename: str, download_dir: str, blocks_num: int, parent=None,
                 startState=0):

        ###################StartState#####################
        #   0 : 正常开始
        #   1 : 启动时自动开始
        #   2 : 已下载完成的
        ##################################################

        super(DownloadGroup, self).__init__(parent=parent)

        self.iconPath = iconPath
        self.url = url
        self.filename = filename
        self.download_dir = download_dir
        self.cache_dir = f"{self.download_dir}/.cache/"
        self.blocks_num = blocks_num
        self.parent = parent
        self.startState = startState

        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:97.0) Gecko/20100101 Firefox/97.0'

        self.mainWindow = self.parent.parent()

        # CreateAnimation
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.OutQuart)

        self.Paused = False # 暂停状态

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
                    Dialog(self.mainWindow, "错误！", "当前目录下有同名文件！请更改文件名或路径后重试！").execSignal.emit()
                    return

                elif __url == url:
                    print("重复下载同一文件！")
                    Dialog(self.mainWindow, "错误！", "重复下载同一文件！").execSignal.emit()
                    return

            if startState == 0:
                # 写入历史
                self.whiteHistory()

        else:
            # 没有文件自己造
            self.domTree = Document()
            self.rootNode = self.domTree.createElement("tasks")
            self.domTree.appendChild(self.rootNode)
            self.whiteHistory()

        # 初始化界面
        self.SetUp()

        # Connect Signal to Slot
        self.openFileBtn.clicked.connect(lambda: startfile(self.download_dir))
        self.pauseBtn.clicked.connect(self.pause)
        self.cancelBtn.clicked.connect(self.cancel)
        self.setTextSignal.connect(self.__setText)

        # Create new Processing to Start this Task
        self.Process = DownloadProcess(self.url, self.filename, self.download_dir, self.blocks_num)
        self.Process.start()

        # Start Thread
        self.__getFileSizeThread = threading.Thread(target=self.__getFileSize, daemon=True) # 获取文件大小
        self.__getFileSizeThread.start()
        threading.Thread(target=self.Superviser, daemon=True).start()  # 开启速度检测线程

    def SetUp(self):
        icon = QPixmap(self.iconPath)

        if not self.startState == 2:
            self.setStyleSheet(".QLabel {color: rgb(70, 70, 70);}")

            self.imgLable = PictureLabel(self, icon)
            self.imgLable.setGeometry(QRect(5, 5, 64, 64))

            self.progressBar = MyProgressBar(self)
            self.progressBar.move(74, 26)
            self.progressBar.resize(492, 21)
            self.progressBar.setValue(100)

            self.openFileBtn = QPushButton(self)
            self.openFileBtn.setGeometry(QRect(441, 50, 71, 21))
            self.openFileBtn.setProperty("round", True)

            self.fileSizeLabel = QLabel(self)
            self.fileSizeLabel.setGeometry(QRect(201, 49, 131, 18))

            self.fileNameLabel = QLabel(self)
            self.fileNameLabel.setGeometry(QRect(75, 5, 389, 18))

            self.speedLabel = QLabel(self)
            self.speedLabel.setGeometry(QRect(75, 49, 131, 18))

            self.timeLabel = QLabel(self)
            self.timeLabel.setGeometry(QRect(306, 49, 131, 18))

            self.stateLabel = QLabel(self)
            self.stateLabel.setGeometry(QRect(74, 25, 492, 21))
            self.stateLabel.setStyleSheet("color: rgb(84, 84, 84)")
            self.stateLabel.setAlignment(Qt.AlignCenter)

            self.pauseBtn = QPushButton(self)
            self.pauseBtn.setGeometry(QRect(521, 50, 21, 21))

            self.threadNumLabel = QLabel(self)
            self.threadNumLabel.setGeometry(QRect(464, 5, 200, 18))

            self.cancelBtn = QPushButton(self)
            self.cancelBtn.setGeometry(QRect(551, 50, 21, 21))

            # SetIcon
            self.pauseIcon = QIcon()
            self.pauseIcon.addFile(getSkinFilename("Icon/暂停.png"), QSize(), QIcon.Normal, QIcon.Off)
            self.playIcon = QIcon()
            self.playIcon.addFile(getSkinFilename("Icon/播放.png"), QSize(), QIcon.Normal, QIcon.Off)

            self.pauseBtn.setIcon(self.pauseIcon)

            # SetText
            self.openFileBtn.setText("打开目录")
            self.stateLabel.setText("正在准备...")
            self.cancelBtn.setText("╳")
            self.fileNameLabel.setText(self.filename)
            # self.fileSizeLabel.setText("大小:%s" % self.__getReadableSize(self.fileSize))
            self.fileSizeLabel.setText("大小:正在获取...")
            self.timeLabel.setText("剩余时间:正在获取...")
            self.threadNumLabel.setText(f"线程数:{self.blocks_num}")
            self.speedLabel.setText("速度:正在获取...")

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
        block_numTextValue = self.domTree.createTextNode(str(self.blocks_num))
        block_numNode.appendChild(block_numTextValue)
        taskNode.appendChild(block_numNode)

        iconNode = self.domTree.createElement("icon")
        iconTextValue = self.domTree.createTextNode(self.iconPath)
        iconNode.appendChild(iconTextValue)
        taskNode.appendChild(iconNode)

        self.rootNode.appendChild(taskNode)

        with open("./history.xml", "w") as f:
            # 缩进 - 换行 - 编码
            self.domTree.writexml(f, addindent='    ', newl='\n', encoding='UTF-8')
            f.close()

    def __get_cache_filenames(self):
        return glob.glob(f"{self.cache_dir}{self.filename}.*.d2l")

    def Superviser(self): # 督导
        REFRESH_INTERVAL = 1  # 每多久输出一次监视状态
        LAG_COUNT = 10  # 计算过去多少次测量的平均速度
        self.__download_record = []
        percentage = 0

        self.setTextSignal.emit(self.threadNumLabel, f"线程数:{self.blocks_num}")

        while True:
            if percentage < 100:
                dwn_size = sum([path.getsize(cachefile) for cachefile in self.__get_cache_filenames()])
                self.__download_record.append({"timestamp": time.time(), "size": dwn_size})
                if len(self.__download_record) > LAG_COUNT:
                    self.__download_record.pop(0)

                s = self.__download_record[-1]["size"] - self.__download_record[0]["size"]
                t = self.__download_record[-1]["timestamp"] - self.__download_record[0]["timestamp"]

                self.__getFileSizeThread.join()

                if not t == 0 and self.Paused == False:
                    speed = s / t
                    readable_speed = self.__getReadableSize(speed)  # 变成方便阅读的样式
                    percentage = self.__download_record[-1]["size"] / self.fileSize * 100
                    status_msg = f"\r[info] {percentage:.1f} % | {readable_speed}/s | {self.blocks_num}"
                    sys.stdout.write(status_msg)
                    # 更改界面
                    self.progressBar.setValue(percentage)

                    self.setTextSignal.emit(self.stateLabel,
                                                  f"正在下载:{percentage:.1f}% ({self.__getReadableSize(self.__download_record[-1]['size'])})")
                    self.setTextSignal.emit(self.speedLabel, f"速度:{readable_speed}/s")
                    if speed == 0:
                        self.setTextSignal.emit(self.timeLabel, "剩余时间:Check...")
                    else:
                        self.setTextSignal.emit(self.timeLabel, f"剩余时间:%s" % timedelta(seconds=round((self.fileSize - self.__download_record[-1]['size']) / speed)))

                time.sleep(REFRESH_INTERVAL)

            elif percentage == 100:
                time.sleep(0.3)
                sewed_size = path.getsize(f"{self.download_dir}/{self.filename}")
                sew_progress = (sewed_size / self.fileSize) * 100
                sys.stdout.write(f"[info] sew_progress {sew_progress} %\n")
                self.setTextSignal.emit(self.stateLabel,
                                              f"正在合并:{sew_progress}% ({self.__getReadableSize(sewed_size)})")
                self.progressBar.setValue(sew_progress)
                if (self.fileSize - sewed_size) == 0:
                    self.setTextSignal.emit(self.stateLabel, "下载完成!")
                    self.progressBar.setValue(sew_progress)

                    logoIcon = QIcon()
                    logoIcon.addFile(logoIcon.addFile(getSkinFilename("Logo.png"), QSize(), QIcon.Normal, QIcon.Off))

                    self.mainWindow.systemTrayIcon.showMessage("Hey--下载完成了!", f"{self.filename} 已完成下载!", logoIcon)
                    self.mainWindow.messageClicked.connect(lambda: startfile(self.download_dir))
                    break
            else:
                self.stop()
                self.clear()

                logoIcon = QIcon()
                logoIcon.addFile(logoIcon.addFile(getSkinFilename("Logo.png"), QSize(), QIcon.Normal, QIcon.Off))

                self.mainWindow.systemTrayIcon.showMessage("Hey--下载失败了!", f"{self.filename} 已失败下载!", logoIcon)
                self.mainWindow.systemTrayIcon.messageClicked.connect(self.mainWindow.show)
                self.setTextSignal.emit(self.stateLabel, "下载完成!")
                break

    def __getReadableSize(self, size):
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        unit_index = 0
        K = 1024.0
        while size >= K:
            size = size / K
            unit_index += 1
        return "%.1f %s" % (size, units[unit_index])

    def __getFileSize(self):
        try:
            # req = request.urlopen(self.url)
            # content_length = req.headers["Content-Length"]
            # req.close()
            # return int(content_length)
            headers = {'User-Agent': self.user_agent}
            req = requests.get(self.url, headers=headers, stream=True, verify=False, proxies=proxy)
            content_length = req.headers["Content-Length"]
            self.fileSize = int(content_length)
            req.close()
            # return int(content_length)
            self.setTextSignal.emit(self.fileSizeLabel, f"大小:{self.__getReadableSize(int(content_length))}")

        except Exception as err:
            self.__bad_url_flag = True
            self.__whistleblower(f"[Error] {err}")
            # return 0
            self.setTextSignal.emit(self.fileSizeLabel, "大小:NULL")

    def __whistleblower(self, saying: str): # 报错时显示错误信息
        # # iPhone 12 mini 每行显示45个字符，等款字体
        # # 这里假设 \r 如果出现一定位于字符串的起始
        # wordsCountOfEachLine = 45
        # if len(saying.replace("\r", "")) > wordsCountOfEachLine:
        #     sys.stdout.write(saying[:wordsCountOfEachLine])
        # else:
        #     sys.stdout.write(saying + " " * (wordsCountOfEachLine - len(saying.replace("\r", ""))))
        print(saying)
        Dialog(self.mainWindow, "错误！", saying).execSignal.emit()

    def __setText(self, obj:QObject, content:str):
        obj.setText(content)

    def pause(self):
        """接受Pause按钮发出的暂停信号并进行操作"""
        if self.Paused == False:  # 没暂停就暂停

            self.Paused = True

            self.pauseBtn.setEnabled(False)
            self.cancelBtn.setEnabled(False)
            self.pauseBtn.setIcon(self.playIcon)
            self.setTextSignal.emit(self.stateLabel, "正在暂停:正在停止线程...")

            self.stop()

            self.pauseBtn.setEnabled(True)
            self.cancelBtn.setEnabled(True)
            self.setTextSignal.emit(self.stateLabel, "正在暂停...")

        elif self.Paused == True:  # 暂停了就开始
            self.pauseBtn.setEnabled(False)
            self.cancelBtn.setEnabled(False)
            self.pauseBtn.setIcon(self.pauseIcon)
            self.setTextSignal.emit(self.stateLabel, "正在开始:正在召回线程...")
            # 再次召集 worker。不调用 start 的原因是希望他继续卡住主线程。
            self.again()

            self.pauseBtn.setEnabled(True)
            self.cancelBtn.setEnabled(True)

            self.Paused = False

    def again(self):
        self.Process = DownloadProcess(self.url, self.filename, self.download_dir, self.blocks_num)
        self.Process.start()

    def stop(self):
        self.Process.kill()

    def cancel(self):
        self.pauseBtn.setEnabled(False)
        self.cancelBtn.setEnabled(False)
        self.setTextSignal.emit(self.stateLabel, "正在取消任务:正在暂停线程...")
        self.Paused = True
        self.stop()
        self.setTextSignal.emit(self.stateLabel, "正在取消任务:正在清理缓存...")

        # Cancel Animation
        self.animation.setEndValue(self.width(), self.y())
        self.animation.start()

        if len(DownGroupBoxesList) == 1:
            del DownGroupBoxesList[0]
        else:
            ID = DownGroupBoxesList.index(self)
            del DownGroupBoxesList[ID]
            for i in range(len(DownGroupBoxesList)):
                DownGroupBoxesList[i].animation.setEndValue(DownGroupBoxesList[i].x(), i * 78 + 5)

        self.clear()
        self.deleteLater()


class DownloadProcess(Process):
    def __init__(self, url: str, filename: str, download_dir: str, blocks_num: int):
        super(DownloadProcess, self).__init__(daemon=True)

        self.url = url
        self.filename = filename
        self.blocks_num = blocks_num
        self.download_dir = download_dir

        self.__bad_url_flag = False
        self.file_size = self.__get_size()

        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:97.0) Gecko/20100101 Firefox/97.0'

    def run(self):
        super(DownloadProcess, self).run()
        if not self.__bad_url_flag:
            # 建立下载目录
            if not os.path.exists(self.download_dir):
                os.makedirs(self.download_dir)
            # 建立缓存目录
            self.cache_dir = f".{os.sep}d2l{os.sep}.cache{os.sep}"
            if not os.path.exists(self.cache_dir):
                os.makedirs(self.cache_dir)
            # 分块下载
            self.startdlsince = time.time()
            self.workers = []  # 装载 DLWorker
            self.AAEK = self.__get_AAEK_from_cache()  # 需要确定 self.file_size 和 self.block_num
            # 测速
            self.__done = threading.Event()
            self.__download_record = []
            # 主进程信号，直到下载结束后解除
            self.__main_thread_done = threading.Event()
            # 显示基本信息
            readable_size = self.__getReadableSize(self.file_size)
            pathfilename = f'{self.download_dir}/{self.filename}'
            sys.stdout.write(
                f"----- Ghost-Downloader [Alpha] -----\n[url] {self.url}\n[path] {pathfilename}\n[size] {readable_size}\n")

        # TODO 尝试整理缓存文件夹内的相关文件
        if not self.__bad_url_flag:
            # 召集 worker
            for start, end in self.__ask_for_work(self.blocks_num):
                worker = self.__give_me_a_worker(start, end)
                self.__whip(worker)
            # 卡住主进程
            self.__main_thread_done.wait()

    def __give_me_a_worker(self, start, end):
        worker = DLWorker(name=f"{self.filename}.{start}",
                          url=self.url, range_start=start, range_end=end, cache_dir=self.cache_dir,
                          finish_callback=self.__on_dlworker_finish,
                          user_agent=self.user_agent)
        return worker

    def __on_dlworker_finish(self, worker: DLWorker):
        assert worker.FINISH_TYPE != ""
        self.workers.remove(worker)
        if worker.FINISH_TYPE == "HELP":  # 外包
            self.__give_back_work(worker)
            self.workaholic(2)
        elif worker.FINISH_TYPE == "DONE":  # 完工
            # 再打一份工，也可能打不到
            self.workaholic(1)
        elif worker.FINISH_TYPE == "RETIRE":  # 撂挑子
            # 把工作添加回 AAEK，离职不管了。
            self.__give_back_work(worker)
        # 下载齐全，开始组装
        if self.workers == [] and self.__get_AAEK_from_cache() == []:
            self.__sew()

    def __get_cache_filenames(self):
        return glob.glob(f"{self.cache_dir}{self.filename}.*.d2l")

    def __get_ranges_from_cache(self):
        # 形如 ./cache/filename.1120.d2l
        ranges = []
        for filename in self.__get_cache_filenames():
            size = os.path.getsize(filename)
            if size > 0:
                cache_start = int(filename.split(".")[-2])
                cache_end = cache_start + size - 1
                ranges.append((cache_start, cache_end))
        ranges.sort(key=lambda x: x[0])  # 排序
        return ranges

    def clear(self):
        # 清除历史
        self.domTree = parse("./history.xml")
        self.rootNode = self.domTree.documentElement

        print(self.rootNode.nodeName)

        tasks = self.rootNode.getElementsByTagName("task")

        for task in tasks:  # 寻找该文件
            __filename = task.getElementsByTagName("filename")[0].childNodes[0].data
            print("filename:", __filename)
            __download_dir = task.getElementsByTagName("download_dir")[0].childNodes[0].data
            print("download_dir", __download_dir)
            __url = task.getElementsByTagName("url")[0].childNodes[0].data
            print("url:", __url)

            print(self.filename, self.download_dir, self.url)

            if __filename == self.filename and __download_dir == self.download_dir and __url == self.url:
                self.rootNode.removeChild(task)
                break

        with open("./history.xml", "w") as f:
            # 缩进 - 换行 - 编码
            self.domTree.writexml(f, addindent='    ', newl='\n', encoding='UTF-8')
            f.close()

        for filename in self.__get_cache_filenames():
            os.remove(filename)

    def __sew(self):
        self.__done.set()
        chunk_size = 10 * 1024 * 1024
        with open(f"{os.path.join(self.download_dir, self.filename)}", "wb") as f:
            for start, _ in self.__get_ranges_from_cache():
                cache_filename = f"{self.cache_dir}{self.filename}.{start}.d2l"
                with open(cache_filename, "rb") as cache_file:
                    data = cache_file.read(chunk_size)
                    while data:
                        f.write(data)
                        f.flush()
                        data = cache_file.read(chunk_size)
        self.clear()
        self.__main_thread_done.set()

    def __getReadableSize(self, size):
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        unit_index = 0
        K = 1024.0
        while size >= K:
            size = size / K
            unit_index += 1
        return "%.1f %s" % (size, units[unit_index])

    def __give_back_work(self, worker: DLWorker):
        """接纳没干完的工作。需要按 size 从小到大排序。"""
        progress = worker.get_progress()
        curser = progress["curser"]
        end = progress["end"]
        if curser <= end:  # 校验一下是否是合理值
            self.AAEK.append((curser, end))
            self.AAEK.sort(key=lambda x: x[0])

    def workaholic(self, n=1):
        """九九六工作狂。如果能申请到，就地解析；申请不到，__give_me_a_worker 会尝试将一个 worker 的工作一分为二；"""
        for s, e in self.__ask_for_work(n):
            worker = self.__give_me_a_worker(s, e)
            self.__whip(worker)

    def __get_size(self):
        try:
            # req = request.urlopen(self.url)
            # content_length = req.headers["Content-Length"]
            # req.close()
            # return int(content_length)
            headers = {'User-Agent': self.user_agent}
            req = requests.get(self.url, headers=headers, stream=True, verify=False, proxies=proxy)
            content_length = req.headers["Content-Length"]
            req.close()
            return int(content_length)
        except Exception:
            self.__bad_url_flag = True
            return 0

    def __share_the_burdern(self, minimum_size=1024 * 1024):
        """找出工作最繁重的 worker，调用他的 help。回调函数中会将他的任务一分为二。"""
        max_size = 0
        max_size_name = ""
        for w in self.workers:
            p = w.get_progress()
            size = p["end"] - p["curser"] + 1
            if size > max_size:
                max_size = size
                max_size_name = w.name
        if max_size >= minimum_size:
            for w in self.workers:
                if w.name == max_size_name:
                    w.help()
                    break

    def __get_AAEK_from_cache(self):
        ranges = self.__get_ranges_from_cache()  # 缓存文件里的数据
        AAEK = []  # 根据 ranges 和 self.file_size 生成 AAEK
        if len(ranges) == 0:
            AAEK.append((0, self.file_size - 1))
        else:
            for i, (start, end) in enumerate(ranges):
                if i == 0:
                    if start > 0:
                        AAEK.append((0, start - 1))
                next_start = self.file_size if i == len(ranges) - 1 else ranges[i + 1][0]
                if end < next_start - 1:
                    AAEK.append((end + 1, next_start - 1))
        return AAEK

    def __increase_ranges_slice(self, ranges: list, minimum_size=1024 * 1024):
        """增加分块数目，小于 minimum_size 就不再分割了"""
        assert len(ranges) > 0
        block_size = [end - start + 1 for start, end in ranges]
        index_of_max = block_size.index(max(block_size))
        start, end = ranges[index_of_max]
        halfsize = block_size[index_of_max] // 2
        if halfsize >= minimum_size:
            new_ranges = [x for i, x in enumerate(ranges) if i != index_of_max]
            new_ranges.append((start, start + halfsize))
            new_ranges.append((start + halfsize + 1, end))
        else:
            new_ranges = ranges
        return new_ranges

    def __ask_for_work(self, worker_num: int):
        """申请工作，返回 [work_range]，从 self.AAEK 中扣除。没工作的话返回 []。"""
        assert worker_num > 0
        task = []
        aaek_num = len(self.AAEK)
        if aaek_num == 0:  # 没任务了
            self.__share_the_burdern()
            return []
        if aaek_num >= worker_num:  # 数量充足，直接拿就行了
            for _ in range(worker_num):
                task.append(self.AAEK.pop(0))
        else:  # 数量不足，需要切割
            slice_num = worker_num - aaek_num  # 需要分割几次
            task = self.AAEK  # 这个时候 task 就不可能是 [] 了
            self.AAEK = []
            for _ in range(slice_num):
                task = self.__increase_ranges_slice(task)
        task.sort(key=lambda x: x[0])
        return task

    def __whip(self, worker: DLWorker):
        """鞭笞新来的 worker，让他去工作"""
        self.workers.append(worker)
        self.workers.sort()
        worker.start()
