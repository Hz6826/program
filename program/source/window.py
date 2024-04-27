import os

from .widget import *


class MainPage(BasicPage):
    """
    主页
    """
    title = "主页"
    subtitle = "常用功能"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(FIF.HOME)


class SettingPage(BasicPage):
    """
    设置页面
    """
    title = "设置"
    subtitle = "设置程序"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(FIF.SETTING)

        self.cardGroup1 = CardGroup("插件", self)
        self.cardGroup2 = CardGroup("外观", self)
        self.cardGroup3 = CardGroup("行为", self)
        self.cardGroup4 = CardGroup("功能", self)

        self.addonSettingCard = AddonSettingCard(self)

        self.themeSettingCard = ThemeSettingCard(self)
        self.colorSettingCard = ColorSettingCard(self)
        self.micaEffectSettingCard = MicaEffectSettingCard(self)

        self.startupSettingCard = StartupSettingCard(self)
        self.traySettingCard = TraySettingCard(self)
        self.hideSettingCard = HideSettingCard(self)

        self.downloadSettingCard = DownloadSettingCard(self)

        self.cardGroup1.addWidget(self.addonSettingCard)

        self.cardGroup2.addWidget(self.themeSettingCard)
        self.cardGroup2.addWidget(self.colorSettingCard)
        self.cardGroup2.addWidget(self.micaEffectSettingCard)

        self.cardGroup3.addWidget(self.startupSettingCard)
        self.cardGroup3.addWidget(self.traySettingCard)
        self.cardGroup3.addWidget(self.hideSettingCard)

        self.cardGroup4.addWidget(self.downloadSettingCard)

        self.vBoxLayout.addWidget(self.cardGroup1, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.cardGroup2, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.cardGroup3, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.cardGroup4, 0, Qt.AlignTop)

        if not (program.WINDOWS_VERSION[0] >= 10 and program.WINDOWS_VERSION[2] >= 22000):
            self.micaEffectSettingCard.hide()


class AboutPage(BasicPage):
    """
    关于页面
    """
    title = "关于"
    subtitle = "关于程序"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(FIF.INFO)

        self.cardGroup1 = CardGroup("关于", self)

        self.updateSettingCard = UpdateSettingCard(self)
        self.helpSettingCard = HelpSettingCard(self)
        self.controlSettingCard = ControlSettingCard(self)
        self.aboutSettingCard = AboutSettingCard(self)

        self.cardGroup1.addWidget(self.updateSettingCard)
        self.cardGroup1.addWidget(self.helpSettingCard)
        self.cardGroup1.addWidget(self.controlSettingCard)
        self.cardGroup1.addWidget(self.aboutSettingCard)

        self.bigInfoCard = BigInfoCard(self, data=False)
        self.bigInfoCard.setImg("Ianzb.png", "https://vip.123pan.cn/1813801926/%E8%B5%84%E6%BA%90/%E4%B8%AA%E4%BA%BA/%E5%A4%B4%E5%83%8F/png/%E5%A4%B4%E5%83%8F%E9%AB%98%E6%B8%85%E9%80%8F%E6%98%8E.png")
        self.bigInfoCard.image.setMinimumSize(150, 150)
        self.bigInfoCard.setTitle(program.AUTHOR_NAME)
        self.bigInfoCard.setInfo("Minecraft玩家，科幻迷，编程爱好者！")
        self.bigInfoCard.addUrl("Github", "https://github.com/Ianzb", FIF.GITHUB)
        self.bigInfoCard.addUrl("Bilibili", "https://space.bilibili.com/1043835434", FIF.LINK)
        self.bigInfoCard.addTag("Minecraft")
        self.bigInfoCard.addTag("编程")
        self.bigInfoCard.addTag("科幻")
        self.bigInfoCard.backButton.deleteLater()
        self.bigInfoCard.mainButton.setText("个人网站")
        self.bigInfoCard.mainButton.clicked.connect(lambda: webbrowser.open(program.AUTHOR_URL))
        self.bigInfoCard.mainButton.setIcon(FIF.LINK)

        self.vBoxLayout.addWidget(self.bigInfoCard, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.cardGroup1, 0, Qt.AlignTop)


class Window(FluentWindow, SignalBase):
    """
    主窗口
    """

    def __init__(self):
        super().__init__()

        self.__initWindow()
        self.__initWidget()
        self.__initActivity()

    def __initWindow(self):
        """
        窗口初始化
        """
        # 外观调整
        setTheme(eval(setting.read("theme")), lazy=True)
        setThemeColor("#0078D4", lazy=True)
        self.navigationInterface.setAcrylicEnabled(True)
        self.setMicaEffectEnabled(setting.read("micaEffect"))
        # 窗口属性
        self.resize(900, 700)
        self.setMinimumSize(700, 500)
        self.setWindowIcon(QIcon(program.ICON))
        self.setWindowTitle(program.TITLE)
        self.navigationInterface.setReturnButtonVisible(False)
        # 窗口居中
        desktop = QApplication.screens()[0].size()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def __initWidget(self):
        """
        组件初始化
        """
        self.mainPage = MainPage(self)
        self.settingPage = SettingPage(self)
        self.aboutPage = AboutPage(self)

        self.addPage(self.mainPage, "top")
        self.addSeparator("top")
        self.addSeparator("bottom")
        self.addPage(self.settingPage, "bottom")
        self.addPage(self.aboutPage, "bottom")

    def __initActivity(self):
        # 报错检测
        sys.excepthook = self.getException
        # 循环监测事件
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timerEvent)
        self.timer.start(250)

        # 托盘组件
        self.tray = Tray(self)
        self.tray.setVisible(setting.read("showTray"))

        # 插件安装
        self.addAddon(f.getInstalledAddonInfo())

    def keyPressEvent(self, QKeyEvent):
        """
        自定义按键事件
        """
        # Esc键
        if QKeyEvent.key() == Qt.Key.Key_Escape:
            if setting.read("hideWhenClose"):
                self.hide()

    def closeEvent(self, QCloseEvent):
        """
        自定义关闭事件
        """
        QCloseEvent.ignore()
        if setting.read("hideWhenClose"):
            self.hide()
        else:
            program.close()

    def getException(self, type, value, traceback):
        """
        报错拦截
        @param type: 报错类型
        @param value: 报错对象
        @param traceback: 报错返回信息
        """
        info = "".join(format_exception(type, value, traceback))
        logging.fatal(f"程序发生异常\n{info}")
        self.messageBox = MessageBox("程序发生异常", info, self)
        self.messageBox.contentLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.messageBox.yesButton.setText("重启")
        self.messageBox.yesButton.setIcon(FIF.SYNC)
        self.messageBox.yesButton.clicked.connect(program.restart)
        self.messageBox.cancelButton.setText("关闭")
        self.messageBox.exec()

    def addPage(self, page, pos: str):
        """
        添加导航栏页面简易版
        @param page: 页面对象
        @param pos: 位置top/scroll/bottom
        """
        self.addSubInterface(page, page.icon, page.objectName(), eval(f"NavigationItemPosition.{pos.upper()}"))

    def addSeparator(self, pos: str):
        """
        添加导航栏分割线简易版
        @param pos: 位置top/scroll/bottom
        """
        self.navigationInterface.addSeparator(eval(f"NavigationItemPosition.{pos.upper()}"))

    def addAddon(self, msg):
        """
        添加插件
        @param data: 数据
        """
        if "id" in msg.keys():
            self.__addAddon(msg)
        else:
            for v in msg.values():
                self.__addAddon(v)

    def removeAddon(self, msg):
        """
        移除插件
        @param data: 数据
        """
        if "id" in msg.keys():
            self.__removeAddon(msg)
        else:
            for v in msg.values():
                self.__removeAddon(v)

    def __addAddon(self, data):
        """
        添加插件
        @param data: 数据
        """
        sys.path = [program.ADDON_PATH] + sys.path
        import importlib
        try:
            lib = importlib.import_module(data["id"])
            self.page = lib.AddonPage(self)
            self.page.setObjectName(data["name"])
            self.navigationInterface.removeWidget(self.page.objectName())
            self.addPage(self.page, "scroll")
            logging.warning(f"插件{data["name"]}安装成功")
            self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "提示", f"插件{data["name"]}安装成功！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.settingPage)
            self.infoBar.show()
        except Exception as ex:
            logging.warning(f"插件{data["name"]}安装失败{ex}")
            self.infoBar = InfoBar(InfoBarIcon.ERROR, "错误", f"插件{data["name"]}安装失败{ex}！", Qt.Orientation.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.settingPage)
            self.infoBar.show()

    def __removeAddon(self, data):
        """
        移除插件
        @param data: 数据
        """
        self.navigationInterface.removeWidget(data["name"])
        f.cmd(f"del /F /Q /S {f.pathJoin(program.ADDON_PATH, data["id"])}", True)
        f.delete(f.pathJoin(program.ADDON_PATH, data["id"]))
        logging.info(f"插件{data["name"]}删除成功")

        self.infoBar = InfoBar(InfoBarIcon.SUCCESS, "提示", f"插件{data["name"]}删除成功！", Qt.Orientation.Vertical, True, 10000, InfoBarPosition.TOP_RIGHT, self.settingPage)
        self.infoBar.show()

    def autoUpdateFinish(self, msg):
        """
        开机自动更新完成解锁组件
        """
        if isinstance(msg, bool):
            self.aboutPage.updateSettingCard.setEnabled(True)
        if isinstance(msg, dict):
            if msg["完成"]:
                self.aboutPage.updateSettingCard.setEnabled(True)

    def timerEvent(self):
        """
        重复运行展示窗口
        """
        if f.existPath(f.pathJoin(program.DATA_PATH, "zb.unlock")):
            f.delete(f.pathJoin(program.DATA_PATH, "zb.unlock"))
            self.show()
        if program.isEXE:
            if program.IS_UNINSTALLABLE:
                if len(f.walkFile(program.INSTALL_PATH, 1)) < 3:
                    with open("remove.bat", "w", encoding="utf-8") as file:
                        file.write(f'\nchoice /t 2 /d y /n \nrmdir /S /Q "{program.INSTALL_PATH}"')
                    os.system("powershell -Command Start-Process -FilePath remove.bat -WindowStyle Hidden")
                    program.close()


logging.debug("window.py初始化成功")
