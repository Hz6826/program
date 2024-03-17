from .preload import *


class Tray(QSystemTrayIcon):
    """
    系统托盘组件
    """

    def __init__(self, window):
        super(Tray, self).__init__(QIcon(program.PROGRAM_ICON))
        self.window = window

        self.setIcon(QIcon(program.PROGRAM_ICON))
        self.setToolTip(program.PROGRAM_TITLE)
        self.installEventFilter(ToolTipFilter(self, 1000))
        self.activated.connect(self.iconClicked)

        self.action1 = Action(FIF.HOME, "打开", triggered=self.window.show)
        self.action2 = Action(FIF.ALIGNMENT, "整理", triggered=self.action2Clicked)
        self.action3 = Action(FIF.LINK, "官网", triggered=lambda: webbrowser.open(program.PROGRAM_URL))
        self.action4 = Action(FIF.SYNC, "重启", triggered=program.restart)
        self.action5 = Action(FIF.CLOSE, "退出", triggered=program.close)

        self.menu = AcrylicMenu()

        self.menu.addAction(self.action1)
        self.menu.addAction(self.action2)
        self.menu.addAction(self.action3)
        self.menu.addAction(self.action4)
        self.menu.addAction(self.action5)

        self.window.mainPage.signalBool.connect(self.threadEvent2)

    def showTrayMessage(self, title, msg):
        super().showMessage(title, msg, QIcon(program.PROGRAM_ICON))

    def iconClicked(self, reason):
        if reason == 3:
            self.trayClickedEvent()
        elif reason == 1:
            self.contextMenuEvent()

    def trayClickedEvent(self):
        if self.window.isHidden():
            self.window.setHidden(False)
            if self.window.windowState() == Qt.WindowState.WindowMinimized:
                self.window.showNormal()
            self.window.raise_()
            self.window.activateWindow()
        else:
            self.window.setHidden(True)

    def contextMenuEvent(self):
        self.menu.exec(QCursor.pos(), ani=True, aniType=MenuAnimationType.PULL_UP)
        self.menu.show()

    def action2Clicked(self):
        self.action2.setEnabled(False)
        self.window.mainPage.button1_1Clicked()

    def threadEvent2(self, msg):
        self.action2.setEnabled(msg)


class BetterScrollArea(ScrollArea):
    """
    优化样式的滚动区域
    """
    signalStr = Signal(str)
    signalInt = Signal(int)
    signalBool = Signal(bool)
    signalList = Signal(list)
    signalDict = Signal(dict)
    signalObject = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("QScrollArea {background-color: rgba(0,0,0,0); border: none}")
        self.view = QWidget(self)
        self.view.setStyleSheet("QWidget {background-color: rgba(0,0,0,0); border: none}")

        self.setWidget(self.view)

        self.vBoxLayout = QVBoxLayout(self.view)
        self.vBoxLayout.setSpacing(30)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.setContentsMargins(36, 20, 36, 36)


class BasicPage(BetterScrollArea):
    """
    页面模板
    """
    title = ""
    subtitle = ""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(self.title)

        self.toolBar = ToolBar(self.title, self.subtitle, self)

        self.setViewportMargins(0, self.toolBar.height(), 0, 0)

        self.icon = None

    def setIcon(self, icon):
        self.icon = icon


class BasicTabPage(BasicPage):
    """
    有多标签页的页面模板
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.toolBar.deleteLater()

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.pivot = Pivot(self)
        self.vBoxLayout.addWidget(self.pivot, 0, Qt.AlignmentFlag.AlignHCenter)

        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.vBoxLayout.addWidget(self.stackedWidget)

    def addPage(self, widget):
        name = widget.objectName()
        widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(name, name, lambda: self.stackedWidget.setCurrentWidget(widget), widget.icon)
        if self.stackedWidget.count() == 1:
            self.stackedWidget.setCurrentWidget(widget)
            self.pivot.setCurrentItem(widget.objectName())

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())


class BasicTab(BasicPage):
    """
    有多标签页模板
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.toolBar.deleteLater()
        self.setViewportMargins(0, 0, 0, 0)


class ToolBar(QWidget):
    """
    页面顶端工具栏
    """

    def __init__(self, title: str, subtitle: str, parent=None):
        """
        @param title: 主标题
        @param subtitle: 副标题
        """
        super().__init__(parent=parent)
        self.setFixedHeight(90)

        self.titleLabel = TitleLabel(title, self)
        self.subtitleLabel = CaptionLabel(subtitle, self)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(36, 22, 36, 12)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addSpacing(4)
        self.vBoxLayout.addWidget(self.subtitleLabel)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)


class StatisticsWidget(QWidget):
    """
    两行信息组件
    """

    def __init__(self, title: str, value: str, parent=None):
        """
        @param title: 标题
        @param value: 值
        """
        super().__init__(parent=parent)
        self.titleLabel = CaptionLabel(title, self)
        self.valueLabel = BodyLabel(value, self)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(16, 0, 16, 0)
        self.vBoxLayout.addWidget(self.valueLabel, 0, Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignBottom)

        setFont(self.valueLabel, 18, QFont.Weight.DemiBold)
        self.titleLabel.setTextColor(QColor(96, 96, 96), QColor(206, 206, 206))


class Image(QLabel):
    """
    图片组件（可实时下载）
    """

    @functools.singledispatchmethod
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedSize(48, 48)
        self.setScaledContents(True)
        self.loading = False

    @__init__.register
    def _(self, path: str, url: str = None, parent=None):
        """
        @param path: 路径
        @param url: 链接
        """
        self.__init__(parent)
        if path:
            self.setImg(path, url)

    def threadEvent1(self, msg):
        if msg:
            self.loading = False
            self.setPixmap(QPixmap(self.path))

    def setImg(self, path: str, url: str = None):
        """
        设置图片
        @param path: 路径
        @param url: 链接
        """
        if url:
            self.loading = True
            self.path = program.cache(path)
            self.url = url
            self.thread1 = NewThread("下载图片", [self.url, self.path])
            self.thread1.signalBool.connect(self.threadEvent1)
            self.thread1.start()
        else:
            self.loading = False
            self.setPixmap(QPixmap(path))


class DisplayCard(ElevatedCardWidget):
    """
    大图片卡片
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(168, 176)
        self.setStyleSheet("QLabel {background-color: rgba(0,0,0,0); border: none;}")

        self.widget = Image(self)

        self.label = CaptionLabel(self)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.widget, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.label, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)

        self.setTheme()
        qconfig.themeChanged.connect(self.setTheme)

    def setTheme(self):
        if isDarkTheme():
            self.setStyleSheet("QLabel {background-color: transparent; color: white}")
        else:
            self.setStyleSheet("QLabel {background-color: transparent; color: black}")

    def setText(self, text: str):
        """
        设置文本
        @param text: 文本
        """
        self.label.setText(text)

    def setDisplay(self, widget):
        """
        设置展示组件
        @param widget: 组件
        """
        self.widget = widget
        self.vBoxLayout.replaceWidget(self.vBoxLayout.itemAt(1).widget(), self.widget)


class LoadingCard(DisplayCard):
    """
    加载中卡片
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.progressRingLoading = IndeterminateProgressRing(self)
        self.setDisplay(self.progressRingLoading)
        self.setText("加载中...")


class GrayCard(QWidget):
    """
    灰色背景组件卡片
    """

    def __init__(self, title: str = None, parent=None, alignment=Qt.AlignmentFlag.AlignLeft):
        """
        @param title: 标题
        """
        super().__init__(parent=parent)

        self.titleLabel = StrongBodyLabel(self)
        if title:
            self.titleLabel.setText(title)
        else:
            self.titleLabel.hide()

        self.card = QFrame(self)
        self.card.setObjectName("GrayCard")

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)
        self.vBoxLayout.setSpacing(12)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(self.card, 0, Qt.AlignmentFlag.AlignTop)

        self.hBoxLayout = QHBoxLayout(self.card)
        self.hBoxLayout.setAlignment(alignment)
        self.hBoxLayout.setSizeConstraint(QHBoxLayout.SizeConstraint.SetMinimumSize)
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(12, 12, 12, 12)

        self.setTheme()
        qconfig.themeChanged.connect(self.setTheme)

    def setTheme(self):
        if isDarkTheme():
            self.setStyleSheet("QLabel {background-color: transparent; color: white}")
            self.card.setStyleSheet("#GrayCard {background-color: rgba(25,25,25,0.5); border:1px solid rgba(20,20,20,0.15); border-radius: 10px}")
        else:
            self.setStyleSheet("QLabel {background-color: transparent; color: black}")
            self.card.setStyleSheet("#GrayCard {background-color: rgba(175,175,175,0.1); border:1px solid rgba(150,150,150,0.15); border-radius: 10px}")

    def addWidget(self, widget: object, spacing=0, alignment=Qt.AlignmentFlag.AlignTop):
        """
        添加组件
        @param widget: 组件
        @param spacing: 间隔
        @param alignment: 对齐方式
        """
        self.hBoxLayout.addWidget(widget, alignment=alignment)
        self.hBoxLayout.addSpacing(spacing)


class BigInfoCard(CardWidget):
    """
    详细信息卡片（资源主页展示）
    """

    def __init__(self, parent=None, url: bool = True, tag: bool = True, data: bool = True):
        """
        @param url: 是否展示链接
        @param tag: 是否展示标签
        @param data: 是否展示数据
        """
        super().__init__(parent)
        self.setMinimumWidth(0)

        self.backButton = TransparentToolButton(FIF.RETURN, self)
        self.backButton.move(8, 8)
        self.backButton.setMaximumSize(32, 32)
        self.backButton.clicked.connect(self.backButtonClicked)

        self.image = Image(self)

        self.titleLabel = TitleLabel(self)

        self.mainButton = PrimaryPushButton("下载", self)
        self.mainButton.clicked.connect(self.mainButtonClicked)
        self.mainButton.setFixedWidth(160)

        self.infoLabel = BodyLabel(self)
        self.infoLabel.setWordWrap(True)

        self.hBoxLayout1 = QHBoxLayout()
        self.hBoxLayout1.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout1.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.hBoxLayout1.addWidget(self.mainButton, 0, Qt.AlignmentFlag.AlignRight)

        self.hBoxLayout2 = FlowLayout(needAni=True)
        self.hBoxLayout2.setAnimation(200)
        self.hBoxLayout2.setSpacing(0)
        self.hBoxLayout2.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.hBoxLayout3 = FlowLayout(needAni=True)
        self.hBoxLayout3.setAnimation(200)
        self.hBoxLayout3.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout3.setSpacing(10)
        self.hBoxLayout3.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.hBoxLayout4 = FlowLayout(needAni=True)
        self.hBoxLayout4.setAnimation(200)
        self.hBoxLayout4.setSpacing(8)
        self.hBoxLayout4.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.vBoxLayout = QVBoxLayout()
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.addLayout(self.hBoxLayout1)

        if url:
            self.vBoxLayout.addSpacing(3)
            self.vBoxLayout.addLayout(self.hBoxLayout2)
        else:
            self.hBoxLayout2.deleteLater()
        if data:
            self.vBoxLayout.addSpacing(20)
            self.vBoxLayout.addLayout(self.hBoxLayout3)
            self.vBoxLayout.addSpacing(20)
        else:
            self.hBoxLayout3.deleteLater()
        self.vBoxLayout.addWidget(self.infoLabel)
        if tag:
            self.vBoxLayout.addSpacing(12)
            self.vBoxLayout.addLayout(self.hBoxLayout4)
        else:
            self.hBoxLayout4.deleteLater()

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setSpacing(30)
        self.hBoxLayout.setContentsMargins(34, 24, 24, 24)
        self.hBoxLayout.addWidget(self.image, 0, Qt.AlignmentFlag.AlignVCenter)
        self.hBoxLayout.addLayout(self.vBoxLayout)

        self.setTheme()
        qconfig.themeChanged.connect(self.setTheme)

    def setTheme(self):
        if isDarkTheme():
            self.setStyleSheet("QLabel {background-color: transparent; color: white}")
        else:
            self.setStyleSheet("QLabel {background-color: transparent; color: black}")

    def backButtonClicked(self):
        self.hide()

    def mainButtonClicked(self):
        pass

    def setTitle(self, text: str):
        """
        设置标题
        @param text: 文本
        """
        self.titleLabel.setText(text)

    def setImg(self, path: str, url: str = None):
        """
        设置图片
        @param path: 路径
        @param url: 链接
        """
        self.image.setImg(path, url)

    def setInfo(self, data: str):
        """
        设置信息
        @param data: 文本
        """
        self.infoLabel.setText(data)

    def addUrl(self, text: str, url: str, icon=None):
        """
        添加链接
        @param text: 文本
        @param url: 链接
        @param icon: 图标
        """
        button = HyperlinkButton(url, text, self)
        if icon:
            button.setIcon(icon)
        self.hBoxLayout2.addWidget(button)

    def addData(self, title: str, data: str | int):
        """
        添加数据
        @param title: 标题
        @param data: 数据
        """
        widget = StatisticsWidget(title, str(data), self)
        if self.hBoxLayout3.count() >= 1:
            seperator = VerticalSeparator(widget)
            seperator.setMinimumHeight(50)
            self.hBoxLayout3.addWidget(seperator)
        self.hBoxLayout3.addWidget(widget)

    def addTag(self, name: str):
        """
        添加标签
        @param name: 名称
        """
        self.tagButton = PillPushButton(name, self)
        self.tagButton.setCheckable(False)
        setFont(self.tagButton, 12)
        self.tagButton.setFixedSize(80, 32)
        self.hBoxLayout4.addWidget(self.tagButton)


class SmallInfoCard(CardWidget):
    """
    普通信息卡片（搜索列表展示）
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(0)
        self.setFixedHeight(73)

        self.image = Image(self)

        self.titleLabel = BodyLabel(self)

        self.info = ["", "", "", ""]
        self.contentLabel1 = CaptionLabel(f"{self.info[0]}\n{self.info[1]}", self)
        self.contentLabel1.setTextColor("#606060", "#d2d2d2")
        self.contentLabel1.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.contentLabel2 = CaptionLabel(f"{self.info[2]}\n{self.info[3]}", self)
        self.contentLabel2.setTextColor("#606060", "#d2d2d2")
        self.contentLabel2.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.mainButton = PushButton("进入", self, FIF.CHEVRON_RIGHT)
        self.mainButton.clicked.connect(self.mainButtonClicked)

        self.vBoxLayout1 = QVBoxLayout()

        self.vBoxLayout1.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout1.setSpacing(0)
        self.vBoxLayout1.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignVCenter)
        self.vBoxLayout1.addWidget(self.contentLabel1, 0, Qt.AlignmentFlag.AlignVCenter)
        self.vBoxLayout1.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.vBoxLayout2 = QVBoxLayout()
        self.vBoxLayout2.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout2.setSpacing(0)
        self.vBoxLayout2.addWidget(self.contentLabel2, 0, Qt.AlignmentFlag.AlignVCenter)
        self.vBoxLayout2.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(20, 11, 11, 11)
        self.hBoxLayout.setSpacing(16)
        self.hBoxLayout.addWidget(self.image)
        self.hBoxLayout.addLayout(self.vBoxLayout1)
        self.hBoxLayout.addStretch(5)
        self.hBoxLayout.addLayout(self.vBoxLayout2)
        self.hBoxLayout.addStretch(0)
        self.hBoxLayout.addWidget(self.mainButton, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.setTheme()
        qconfig.themeChanged.connect(self.setTheme)

    def setTheme(self):
        if isDarkTheme():
            self.setStyleSheet("QLabel {background-color: transparent; color: white}")
        else:
            self.setStyleSheet("QLabel {background-color: transparent; color: black}")

    def mainButtonClicked(self):
        pass

    def setTitle(self, text: str):
        """
        设置标题
        @param text: 文本
        """
        self.titleLabel.setText(text)

    def setImg(self, path: str, url: str = None):
        """
        设置图片
        @param path: 路径
        @param url: 链接
        """
        self.image.setImg(path, url)

    def setInfo(self, data: str, pos: int):
        """
        设置信息
        @param data: 文本
        @param pos: 位置：0 左上 1 左下 2 右上 3 右下
        """
        data = data.replace(r"\n", "").replace(r"\r", "").replace(r"\t", "").strip()
        self.info[pos] = data
        self.contentLabel1.setText(f"{self.info[0]}\n{self.info[1]}".strip())
        self.contentLabel2.setText(f"{self.info[2]}\n{self.info[3]}".strip())

        self.contentLabel1.adjustSize()


class CardGroup(QWidget):
    """
    卡片组
    """

    @functools.singledispatchmethod
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setMinimumSize(0, 0)

        self.titleLabel = StrongBodyLabel(self)
        self.vBoxLayout = QVBoxLayout(self)
        self.cardLayout = ExpandLayout()

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.setSpacing(0)
        self.cardLayout.setContentsMargins(0, 0, 0, 0)
        self.cardLayout.setSpacing(2)

        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addSpacing(12)
        self.vBoxLayout.addLayout(self.cardLayout, 1)

        FluentStyleSheet.SETTING_CARD_GROUP.apply(self)
        self.titleLabel.adjustSize()

    @__init__.register
    def _(self, title: str = None, parent=None):
        self.__init__(parent)
        if title:
            self.titleLabel.setText(title)

    def addWidget(self, card):
        self.card = card
        self.card.setParent(self)
        self.cardLayout.addWidget(self.card)

    def setTitle(self, text: str):
        """
        设置标题
        @param text: 文本
        """
        self.titleLabel.setText(text)

    def deleteTitle(self):
        """
        删除标题
        """
        self.titleLabel.deleteLater()

    def setTitleEnabled(self, enabled: bool):
        """
        是否展示标题
        @param enabled: 是否
        """
        self.titleLabel.setHidden(not enabled)


class DownloadWidget(QWidget):
    """
    下载文件ui接口
    """

    def __init__(self, link: str, name: str, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.name = name
        self.link = link

        self.thread1 = NewThread("下载文件", (link, name))
        self.thread1.signalInt.connect(self.thread1_1)
        self.thread1.signalBool.connect(self.thread1_2)
        self.thread1.start()

        self.progressBar = ProgressBar(self.parent)
        self.progressBar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setMinimumWidth(200)

        self.infoBar = InfoBar(InfoBarIcon.INFORMATION, "下载", f"正在下载文件 {name}", Qt.Orientation.Vertical, True, -1, InfoBarPosition.TOP_RIGHT, self.parent)
        self.infoBar.addWidget(self.progressBar)
        self.infoBar.show()
        self.infoBar.closeButton.clicked.connect(self.thread1.cancel)

    def thread1_1(self, msg):
        try:
            self.infoBar.contentLabel.setText(f"正在下载文件 {self.name}")
            self.progressBar.setValue(msg)
        except:
            return
        if msg == 100:
            self.infoBar.contentLabel.setText(f"{self.name} 下载成功")
            self.infoBar.closeButton.click()

            self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "下载", f"资源 {self.name} 下载成功", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent)
            self.infoBar.show()
            self.button1 = PushButton("打开目录", self.parent, FIF.FOLDER)
            self.button1.clicked.connect(self.button1Clicked)
            self.infoBar.addWidget(self.button1)

            self.progressBar.setValue(0)
            self.progressBar.deleteLater()

    def thread1_2(self, msg):
        if not msg:
            try:
                self.infoBar.closeButton.click()
            except:
                self.thread1.cancel()
            self.infoBar = InfoBar(InfoBarIcon.ERROR, "错误", f"下载失败", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent)
            self.infoBar.show()

    def button1Clicked(self):
        f.showFile(setting.read("downloadPath"))
        self.infoBar.closeButton.click()


logging.debug("custom.py初始化成功")
