from main_interface import *
from minecraft_interface import *
from setting_interface import *


class Tray(QSystemTrayIcon):
    def __init__(self, UI):
        super(Tray, self).__init__()
        self.window = UI
        self.menu = RoundMenu()
        self.menu.addAction(Action(FIF.HOME, "打开", triggered=lambda: self.window.show()))
        self.menu.addAction(Action(FIF.ALIGNMENT, "整理", triggered=lambda: self.window.mainInterface.btn1_1()))
        self.menu.addAction(Action(FIF.LINK, "官网", triggered=lambda: webbrowser.open(program_url)))
        self.menu.addAction(Action(FIF.CLOSE, "退出", triggered=lambda: self.triggered()))
        self.setIcon(QIcon("img/logo.png"))
        self.setToolTip(title_name)
        self.activated.connect(self.clickedIcon)
        self.show()

    def clickedIcon(self, reason):
        if reason == 3:
            self.trayClickedEvent()
        elif reason == 1:
            self.contextMenuEvent()

    def trayClickedEvent(self):
        if self.window.isHidden():
            self.window.setHidden(False)
            if self.window.windowState() == QtCore.Qt.WindowMinimized:
                self.window.showNormal()
            self.window.raise_()
            self.window.activateWindow()
            logging.info("展示窗口")
        else:
            self.window.setHidden(True)
            logging.info("隐藏窗口")

    def triggered(self):
        self.deleteLater()
        qApp.quit()

    def contextMenuEvent(self):
        self.menu.exec(QCursor.pos(), ani=True, aniType=MenuAnimationType.PULL_UP)


class MainWindow(FluentWindow):

    def __init__(self):
        super().__init__()
        # 窗口初始化
        self.resize(800, 600)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon("img/logo.png"))
        self.setWindowTitle(title_name)

        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        QApplication.processEvents()
        # 组件设置
        self.tray = Tray(self)
        self.mainInterface = mainInterface(self)
        self.minecraftInterface = minecraftInterface(self)
        self.settingInterface = settingInterface(self)

        signalBus.switchToSampleCard.connect(self.switchToSample)
        signalBus.supportSignal.connect(self.onSupport)
        # 设置导航栏
        self.navigationInterface.addSeparator()

        self.addSubInterface(self.mainInterface, FIF.HOME, "主页", NavigationItemPosition.SCROLL)
        self.addSubInterface(self.minecraftInterface, FIF.GAME, "Minecraft", NavigationItemPosition.SCROLL)
        self.navigationInterface.addSeparator(NavigationItemPosition.BOTTOM)
        self.navigationInterface.addWidget(
            routeKey="avatar",
            widget=NavigationAvatarWidget(zb_name, "img/zb.png"),
            onClick=self.onSupport,
            position=NavigationItemPosition.BOTTOM
        )

        self.addSubInterface(self.settingInterface, FIF.SETTING, "设置", NavigationItemPosition.BOTTOM)

        self.splashScreen.finish()
        self.thread = newThread(8)
        self.thread.signal.connect(self.ifShow)
        self.thread.start()

    def ifShow(self, msg):
        if msg == "展示":
            self.show()

    def onSupport(self):
        w = MessageBox(
            "欢迎使用zb小程序！",
            "作者：" + zb_name,
            self
        )
        w.yesButton.setText("前往作者网站")
        w.cancelButton.setText("取消")
        if w.exec():
            webbrowser.open(zb_url)

    def switchToSample(self, routeKey, index):
        interfaces = self.findChildren(GalleryInterface)
        for w in interfaces:
            if w.objectName() == routeKey:
                self.stackedWidget.setCurrentWidget(w, False)
                w.scrollToCard(index)

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == QtCore.Qt.Key_Escape:
            logging.info("按下Esc键")
            self.hide()

    def closeEvent(self, QCloseEvent):
        QCloseEvent.ignore()
        logging.info("隐藏窗口")
        self.hide()