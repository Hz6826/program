import sys, os

sys.path = [os.path.dirname(sys.argv[0])] + sys.path
from source.custom import *

os.chdir(os.path.dirname(__file__))

try:
    from beta.source.custom import *
except:
    pass
from .api import *


class MyThread(QThread):
    """
    多线程模块
    """
    signalStr = pyqtSignal(str)
    signalInt = pyqtSignal(int)
    signalBool = pyqtSignal(bool)
    signalList = pyqtSignal(list)
    signalDict = pyqtSignal(dict)
    signalObject = pyqtSignal(object)

    def __init__(self, mode: str, data=None, parent: QWidget = None):
        super().__init__(parent=parent)
        self.mode = mode
        self.data = data
        self.isCancel = False

    def run(self):
        if self.mode == "搜索资源":
            try:
                data = searchMod(self.data[0], self.data[1], self.data[2], type=self.data[3])
                self.signalList.emit(data)
            except Exception as ex:
                self.signalBool.emit(False)
        if self.mode == "下载资源":
            try:
                path = f.pathJoin(setting.read("downloadPath"), self.data[0])
                if f.existPath(path):
                    i = 1
                    while f.existPath(f.pathJoin(f.splitPath(path, 3), f.splitPath(path, 1) + " (" + str(i) + ")" + f.splitPath(path, 2))):
                        i = i + 1
                    path = f.pathJoin(f.splitPath(path, 3), f.splitPath(path, 1) + " (" + str(i) + ")" + f.splitPath(path, 2))
                logging.debug(f"开始下载文件{path}")
                path += ".zb.mod.downloading"
                url = self.data[1]
                self.signalStr.emit(path)
                response = requests.get(url, headers=program.REQUEST_HEADER, stream=True, timeout=(5, 10))
                size = 0
                file_size = int(response.headers["content-length"])
                if response.status_code == 200:
                    with open(path, "wb") as file:
                        for data in response.iter_content(256):
                            if self.isCancel:
                                self.signalBool.emit(True)
                                return
                            file.write(data)
                            size += len(data)
                            self.signalInt.emit(int(100 * size / file_size))
                logging.debug(f"文件{path}下载成功")
            except:
                self.signalBool.emit(False)
        if self.mode == "获得游戏版本列表":
            try:
                self.signalList.emit(getVersionList())
            except:
                self.signalBool.emit(False)
        if self.mode == "获得资源信息":
            try:
                data = getModInfo(self.data[0], self.data[1])
                self.signalDict.emit(data)
            except Exception as ex:
                self.signalBool.emit(False)
        if self.mode == "获得资源文件":
            try:
                data = getModFile(self.data[0], self.data[1], self.data[2], self.data[3])
                self.signalDict.emit(data)
            except Exception as ex:
                self.signalBool.emit(False)

    def cancel(self):
        logging.debug("取消下载")
        self.isCancel = True


class SmallModInfoCard(SmallInfoCard):
    """
    资源信息小卡片
    """
    signalStr = pyqtSignal(str)
    signalInt = pyqtSignal(int)
    signalBool = pyqtSignal(bool)
    signalList = pyqtSignal(list)
    signalDict = pyqtSignal(dict)
    signalObject = pyqtSignal(object)

    def __init__(self, data: dict, source: str, parent: QWidget = None):
        """
        @param data: 资源数据
        @param source: 资源来源
        """
        super().__init__(parent)

        self.data = data
        self.source = source

        self.mainButton.deleteLater()

        self.setImg(f"{self.source}/{f.removeIllegalPath(self.data["名称"])}.png", self.data["图标"])
        self.setTitle(f"{self.data["名称"]}")

        self.setInfo(self.data["介绍"], 0)
        self.setInfo(f"下载量：{f.numberAddUnit(self.data["下载量"])}", 1)
        self.setInfo(f"游戏版本：{self.data["游戏版本"][0] + "-" + self.data["游戏版本"][-1] if len(self.data["游戏版本"]) > 1 else self.data["游戏版本"][0] if len(self.data["游戏版本"]) > 0 else "无"}", 2)
        self.setInfo(f"更新日期：{self.data["更新日期"]}", 3)

    def mousePressEvent(self, event):
        self.signalDict.emit(self.data)

    def thread3(self, msg):
        if msg:
            f.delete(self.filePath)
        self.mainButton.setEnabled(True)

    def button1Clicked(self):
        f.startFile(setting.read("downloadPath"))
        self.infoBar.closeButton.click()


class BigModInfoCard(BigInfoCard):
    """
    资源信息大卡片
    """
    signalStr = pyqtSignal(str)
    signalInt = pyqtSignal(int)
    signalBool = pyqtSignal(bool)
    signalList = pyqtSignal(list)
    signalDict = pyqtSignal(dict)
    signalObject = pyqtSignal(object)

    def __init__(self, data: dict, parent: QWidget = None, widgets=[]):
        """
        @param data: 资源数据
        """
        super().__init__(parent)
        self.data = data

        self.loadingCard = widgets[0]
        self.vBoxLayout = widgets[1]

        self.mainButton.deleteLater()

        self.loadingCard.setText("加载中")
        self.loadingCard.show()

        self.titleLabel.setMaximumWidth(500)
        self.titleLabel.setMinimumWidth(400)

        self.setTitle(data["名称"])
        self.setInfo(data["介绍"])
        self.setImg(f"{data["来源"]}/{f.removeIllegalPath(data["名称"])}.png", data["图标"])
        self.addData("作者", data["作者"])
        self.addData("下载量", f.numberAddUnit(data["下载量"]))
        self.addData("发布日期", data["发布日期"])
        self.addData("更新日期", data["更新日期"])

        self.cardGroup = CardGroup("文件", self)
        self.vBoxLayout.insertWidget(3, self.cardGroup)
        self.cardGroup.hide()

        self.thread1 = MyThread("获得资源信息", [data["id"], data["来源"]])
        self.thread1.signalDict.connect(self.thread1_1)
        self.thread1.signalBool.connect(self.thread1_2)
        self.thread1.start()

    def thread1_1(self, msg):
        self.setTitle(msg["名称"])
        self.setInfo(msg["介绍"])
        self.setImg(f"{msg["来源"]}/{f.removeIllegalPath(msg["名称"])}.png", msg["图标"])
        self.addUrl(msg["来源"], msg["网站链接"], FIF.LINK)
        if msg["源代码链接"]:
            self.addUrl("源代码", msg["源代码链接"], FIF.GITHUB)
        self.addUrl("MC百科", f"https://search.mcmod.cn/s?key={msg["名称"]}", FIF.SEARCH)

        for i in msg["加载器"]:
            self.addTag(i)

        self.label1 = StrongBodyLabel("版本筛选", self)

        self.comboBox1 = AcrylicComboBox(self)
        self.comboBox1.setPlaceholderText("版本")
        self.comboBox1.addItems(["全部"] + msg["游戏版本"][::-1])
        self.comboBox1.setCurrentIndex(0)
        self.comboBox1.setToolTip("选择资源版本")
        self.comboBox1.installEventFilter(ToolTipFilter(self.comboBox1, 1000))
        self.comboBox1.setMaxVisibleItems(15)
        self.comboBox1.currentIndexChanged.connect(self.getFileInfo)

        self.label2 = StrongBodyLabel("加载器", self)

        self.comboBox2 = AcrylicComboBox(self)
        self.comboBox2.setPlaceholderText("加载器版本")
        self.comboBox2.addItems(["全部"] + msg["加载器"])
        self.comboBox2.setCurrentIndex(0)
        self.comboBox2.setToolTip("选择加载器版本")
        self.comboBox2.installEventFilter(ToolTipFilter(self.comboBox1, 1000))
        self.comboBox2.currentIndexChanged.connect(self.getFileInfo)

        self.card1 = GrayCard("筛选")
        self.card1.addWidget(self.label1, alignment=Qt.AlignCenter)
        self.card1.addWidget(self.comboBox1)
        self.card1.addWidget(self.label2, alignment=Qt.AlignCenter)
        self.card1.addWidget(self.comboBox2)

        self.vBoxLayout.insertWidget(1, self.card1)

        self.getFileInfo()

    def getFileInfo(self):
        self.cardGroup.hide()
        self.loadingCard.setText("加载中")
        self.loadingCard.show()
        self.comboBox1.setEnabled(False)
        self.comboBox2.setEnabled(False)

        self.thread2 = MyThread("获得资源文件", [self.data["id"], self.data["来源"], self.comboBox1.currentText(), self.comboBox2.currentText()])
        self.thread2.signalDict.connect(self.thread2_1)
        self.thread2.signalBool.connect(self.thread2_2)
        self.thread2.start()

    def thread1_2(self, msg):
        if not msg:
            self.backButtonClicked()
            self.loadingCard.hide()

    def backButtonClicked(self):
        self.signalBool.emit(True)
        try:
            self.card1.deleteLater()
        except:
            pass
        self.cardGroup.deleteLater()
        self.deleteLater()

    def thread2_1(self, msg):
        self.cardGroup.deleteLater()
        self.cardGroup = CardGroup("文件", self)
        if len(msg.keys()) == 0:
            self.cardGroup.setTitle("无筛选结果")
        self.vBoxLayout.insertWidget(3, self.cardGroup)
        i = 0
        for k in msg.keys():
            if k == self.comboBox1.currentText() or self.comboBox1.currentText() == "全部":
                self.cardGroup.addWidget(StrongBodyLabel(k, self))
                for v in msg[k]:
                    self.cardGroup.addWidget(SmallFileInfoCard(v))
                    if i > 50:
                        break
                    i += 1
        self.cardGroup.show()
        self.loadingCard.hide()
        self.comboBox1.setEnabled(True)
        self.comboBox2.setEnabled(True)

    def thread2_2(self, msg):
        if not msg:
            self.loadingCard.setText("加载失败")
            self.loadingCard.show()


class SmallFileInfoCard(SmallInfoCard):
    """
    文件信息小卡片
    """
    signalStr = pyqtSignal(str)
    signalInt = pyqtSignal(int)
    signalBool = pyqtSignal(bool)
    signalList = pyqtSignal(list)
    signalDict = pyqtSignal(dict)
    signalObject = pyqtSignal(object)

    def __init__(self, data: dict, parent: QWidget = None):
        """
        @param data: 资源数据
        """
        super().__init__(parent)
        self.data = data

        self.image.deleteLater()

        self.setTitle(f"{data["名称"]} · {data["版本类型"]}")
        self.setInfo("、".join(data["加载器"]) + (" | " if len(data["加载器"]) > 0 else "") + ("、".join(data["游戏版本"]) if len(data["游戏版本"]) <= 10 else f"支持{data["游戏版本"][0]}-{data["游戏版本"][-1]}共{len(data["游戏版本"])}个版本"), 0)
        self.setInfo(f"文件大小：{f.fileSizeAddUnit(data["文件大小"])}", 1)
        self.setInfo(f"下载量：{f.numberAddUnit(data["下载量"])}", 2)
        self.setInfo(f"更新日期：{data["更新日期"]}", 3)

        self.mainButton.setText("下载")
        self.mainButton.setIcon(FIF.DOWNLOAD)

        if not self.data["下载链接"]:
            self.mainButton.setEnabled(False)

    def mainButtonClicked(self):
        if not self.data["下载链接"]:
            self.infoBar = InfoBar(InfoBarIcon.WARNING, "警告", "该文件暂无下载链接，请更换版本或更换下载源重试！", Qt.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
            self.infoBar.show()
            return
        self.mainButton.setEnabled(False)

        self.thread1 = MyThread("下载资源", (self.data["文件名称"], self.data["下载链接"]))
        self.thread1.signalStr.connect(self.thread1_1)
        self.thread1.signalInt.connect(self.thread1_2)
        self.thread1.signalBool.connect(self.thread1_3)
        self.thread1.start()

        self.progressBar = ProgressBar(self)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setMinimumWidth(200)

        self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "下载", f"正在下载资源 {self.data["名称"]}", Qt.Vertical, True, -1, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
        self.infoBar.addWidget(self.progressBar)
        self.infoBar.show()
        self.infoBar.closeButton.clicked.connect(self.thread1.cancel)

    def thread1_1(self, msg):
        self.filePath = msg

    def thread1_2(self, msg):
        try:
            self.infoBar.contentLabel.setText(f"正在下载资源 {self.data["名称"]}")
            self.progressBar.setValue(msg)
        except:
            return
        if msg == 100:
            f.moveFile(self.filePath, self.filePath.replace(".zb.mod.downloading", ""))

            self.infoBar.contentLabel.setText(f"{self.data["名称"]} 下载成功")
            self.infoBar.closeButton.click()

            self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "下载", f"资源 {self.data["名称"]} 下载成功", Qt.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
            self.infoBar.show()
            self.button1 = PushButton("打开目录", self, FIF.FOLDER)
            self.button1.clicked.connect(self.button1Clicked)
            self.infoBar.addWidget(self.button1)

            self.progressBar.setValue(0)
            self.progressBar.deleteLater()
            self.mainButton.setEnabled(True)

    def thread1_3(self, msg):
        if msg:
            f.delete(self.filePath)
        else:
            self.infoBar.closeButton.click()
            self.infoBar = InfoBar(InfoBarIcon.ERROR, "错误", f"下载失败", Qt.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
            self.infoBar.show()
        self.mainButton.setEnabled(True)

    def button1Clicked(self):
        f.startFile(setting.read("downloadPath"))
        self.infoBar.closeButton.click()


class FileManageTab(BasicTab):
    """
    插件第二页面
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("资源管理")


class AddonTab(BasicTab):
    """
    插件主页面
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("资源下载")

        self.vBoxLayout.setSpacing(8)

        self.lineEdit = AcrylicSearchLineEdit(self)
        self.lineEdit.setPlaceholderText("资源名称")
        self.lineEdit.setToolTip("搜索资源，数据来源：\n CurseForge\n Modrinth")
        self.lineEdit.installEventFilter(ToolTipFilter(self.lineEdit, 1000))
        self.lineEdit.setMaxLength(50)
        self.lineEdit.returnPressed.connect(self.lineEditReturnPressed)
        self.lineEdit.searchButton.clicked.connect(self.searchButtonClicked)
        self.lineEdit.searchButton.setEnabled(True)

        self.label1 = StrongBodyLabel("数据源", self)

        self.comboBox1 = AcrylicComboBox(self)
        self.comboBox1.setPlaceholderText("下载应用来源")
        self.comboBox1.addItems(["CurseForge", "Modrinth"])
        self.comboBox1.setCurrentIndex(0)
        self.comboBox1.setToolTip("选择下载应用来源")
        self.comboBox1.installEventFilter(ToolTipFilter(self.comboBox1, 1000))
        self.comboBox1.currentIndexChanged.connect(self.searchButtonClicked)

        self.label2 = StrongBodyLabel("版本", self)

        self.comboBox2 = AcrylicComboBox(self)
        self.comboBox2.setPlaceholderText("版本")
        self.comboBox2.addItems(["全部"])
        self.comboBox2.setCurrentIndex(0)
        self.comboBox2.setToolTip("选择资源版本")
        self.comboBox2.installEventFilter(ToolTipFilter(self.comboBox2, 1000))
        self.comboBox2.setMaxVisibleItems(15)
        self.comboBox2.currentIndexChanged.connect(self.searchButtonClicked)

        self.label3 = StrongBodyLabel("类型", self)

        self.comboBox3 = AcrylicComboBox(self)
        self.comboBox3.setPlaceholderText("类型")
        self.comboBox3.addItems(list(CURSEFORGE_TYPE.keys()))
        self.comboBox3.setCurrentIndex(0)
        self.comboBox3.setToolTip("选择资源类型")
        self.comboBox3.installEventFilter(ToolTipFilter(self.comboBox3, 1000))
        self.comboBox3.setMaxVisibleItems(15)
        self.comboBox3.currentIndexChanged.connect(self.searchButtonClicked)

        self.card1 = GrayCard("搜索")
        self.card1.addWidget(self.lineEdit)

        self.card2 = GrayCard("筛选")
        self.card2.addWidget(self.label1, alignment=Qt.AlignCenter)
        self.card2.addWidget(self.comboBox1)
        self.card2.addWidget(self.label2, alignment=Qt.AlignCenter)
        self.card2.addWidget(self.comboBox2)
        self.card2.addWidget(self.label3, alignment=Qt.AlignCenter)
        self.card2.addWidget(self.comboBox3)

        self.loadingCard = LoadingCard(self)
        self.loadingCard.hide()

        self.vBoxLayout.addWidget(self.card1)
        self.vBoxLayout.addWidget(self.card2)
        self.vBoxLayout.addWidget(self.loadingCard, 0, Qt.AlignCenter)

        self.cardGroup1 = CardGroup(self.view)
        self.vBoxLayout.addWidget(self.cardGroup1)

        self.thread1 = MyThread("获得游戏版本列表")
        self.thread1.signalList.connect(self.thread1_1)
        self.thread1.signalBool.connect(self.thread1_2)
        self.thread1.start()

        self.loadingCard.setText("正在获得游戏版本列表")
        self.loadingCard.show()
        self.lineEdit.setEnabled(False)
        self.comboBox1.setEnabled(False)
        self.comboBox2.setEnabled(False)
        self.comboBox3.setEnabled(False)

        # self.parent().gamePage.addPage(FileManageTab())

    def lineEditReturnPressed(self):
        self.lineEdit.searchButton.click()

    def searchButtonClicked(self):
        if [self.comboBox1.currentText(), self.comboBox3.currentText()] == ["Modrinth", "地图"]:
            self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "提示", f"Modrinth不支持搜索地图类资源", Qt.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent().parent().parent().parent())
            self.infoBar.show()
            return
        self.cardGroup1.deleteLater()
        self.cardGroup1 = CardGroup(self.view)
        self.vBoxLayout.addWidget(self.cardGroup1)

        self.cardGroup1.setTitleEnabled(False)
        self.lineEdit.setEnabled(False)
        self.comboBox1.setEnabled(False)
        self.comboBox2.setEnabled(False)
        self.comboBox3.setEnabled(False)

        self.loadingCard.setText("搜索中...")
        self.loadingCard.show()

        self.thread2 = MyThread("搜索资源", [self.lineEdit.text(), self.comboBox1.currentText(), self.comboBox2.currentText(), self.comboBox3.currentText()])
        self.thread2.signalList.connect(self.thread2_1)
        self.thread2.signalBool.connect(self.thread2_2)
        self.thread2.start()

    def thread1_1(self, msg):
        self.loadingCard.hide()
        self.comboBox2.addItems(msg)
        self.lineEdit.setEnabled(True)
        self.comboBox1.setEnabled(True)
        self.comboBox2.setEnabled(True)
        self.comboBox3.setEnabled(True)
        self.lineEdit.searchButton.click()

    def thread1_2(self, msg):
        if not msg:
            self.comboBox2.addItems(RELEASE_VERSIONS)

    def thread2_1(self, msg):
        self.loadingCard.hide()
        for i in msg:
            self.infoCard = SmallModInfoCard(i, self.comboBox1.currentText())
            self.infoCard.signalDict.connect(self.showModPage)
            self.vBoxLayout.addWidget(self.infoCard, 0, Qt.AlignTop)
            self.cardGroup1.addWidget(self.infoCard)
        if msg:
            self.cardGroup1.setTitle(f"搜索结果（{len(msg)}个）")
        else:
            self.cardGroup1.setTitle(f"无搜索结果")
        self.cardGroup1.setTitleEnabled(True)

        self.lineEdit.setEnabled(True)
        self.comboBox1.setEnabled(True)
        self.comboBox2.setEnabled(True)
        self.comboBox3.setEnabled(True)

    def thread2_2(self, msg):
        if not msg:
            self.loadingCard.setText("搜索失败！")
            self.loadingCard.show()

            self.lineEdit.setEnabled(True)
            self.comboBox1.setEnabled(True)
            self.comboBox2.setEnabled(True)
            self.comboBox3.setEnabled(True)

    def showModPage(self, msg):
        """
        展示资源页面
        """
        self.cardGroup1.hide()
        self.card1.hide()
        self.card2.hide()

        self.bigModInfoCard = BigModInfoCard(msg, self, [self.loadingCard, self.vBoxLayout])
        self.bigModInfoCard.signalBool.connect(self.hideModPage)
        self.vBoxLayout.insertWidget(0, self.bigModInfoCard)

    def hideModPage(self, msg):
        """
        隐藏资源页面
        """
        self.loadingCard.hide()
        self.vBoxLayout.removeWidget(self.bigModInfoCard)
        self.cardGroup1.show()
        self.card1.show()
        self.card2.show()