from .base import *


class DownloadWidget(QWidget):
    """
    下载文件ui接口
    """
    signalFinished = pyqtSignal(object)
    signalRate = pyqtSignal(object)
    signalPath = pyqtSignal(object)

    def __init__(self, url: str, path: str, threadPool: QThreadPool, parent=None):
        """
        下载文件ui接口
        @param url: 链接
        @param path: 文件完整路径或所在路径
        @param threadPool: 线程池
        @param parent: 父组件
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.path = path
        self.url = url
        self.resultPath = ""

        if f.isDir(self.path):
            self.path = f.joinPath(self.path, f.getFileNameFromUrl(self.url))

        self.multiDownloadThread = threadPool.submit(self.download)
        self.signalFinished.connect(self.downloadFinished)
        self.signalRate.connect(self.downloading)
        self.signalPath.connect(self.setResultPath)

        self.progressBar = ProgressBar()
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setMinimumWidth(200)

        self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "下载", f"正在下载文件{f.splitPath(self.path, 0)}...", Qt.Orientation.Vertical, True, -1, InfoBarPosition.TOP_RIGHT, self.parent)
        self.infoBar.addWidget(self.progressBar)
        self.infoBar.show()

    def download(self):
        from time import sleep
        self.d = MultiDownload(self.url, self.path, False, True, ".downloading", f.REQUEST_HEADER)
        self.infoBar.closeButton.clicked.connect(self.d.stop)

        while True:
            sleep(0.1)
            if self.d.result != "downloading":
                self.signalFinished.emit(self.d.result)
                if self.d.result == "finished":
                    self.signalPath.emit(self.d.resultPath)
                break
            self.signalRate.emit(self.d.rate)

    def downloading(self, msg):
        try:
            self.progressBar.setValue(msg)
        except:
            return

    def downloadFinished(self, msg):
        try:
            self.infoBar.close()
        except:
            pass
        if msg == "skipped":
            self.infoBar = InfoBar(InfoBarIcon.ERROR, "下载错误", f"文件{f.splitPath(self.path, 0)}已取消下载！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent)
            self.infoBar.show()
        elif msg == "failed":
            self.infoBar = InfoBar(InfoBarIcon.ERROR, "下载错误", f"文件{f.splitPath(self.path, 0)}下载失败！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent)
            self.infoBar.show()
        elif msg == "finished":
            self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "下载成功", f"文件{f.splitPath(self.path, 0)}下载成功！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent)
            self.infoBar.show()
        self.progressBar.hide()

    def setResultPath(self, msg):
        self.resultPath = msg
