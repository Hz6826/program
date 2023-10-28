from gallery_interface import *


class settingInterface(ScrollArea):
    checkUpdateSig = pyqtSignal()
    musicFoldersChanged = pyqtSignal(list)
    acrylicEnableChanged = pyqtSignal(bool)
    downloadFolderChanged = pyqtSignal(str)
    minimizeToTrayChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # 组件设置
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        self.settingLabel = QLabel("设置", self)
        self.personalGroup = SettingCardGroup("个性化", self.scrollWidget)
        self.themeCard = OptionsSettingCard(
            FIF.BRUSH,
            "选择模式",
            "更改程序中显示的颜色",
            texts=[
                "浅色", "深色",
                "跟随系统设置"
            ],
            parent=self.personalGroup
        )
        self.themeColorCard = CustomColorSettingCard(
            FIF.PALETTE,
            "主题色",
            "改变程序的主题颜色",
            self.personalGroup
        )
        self.checkBoxCard = checkBoxSettingCard(
            "",
            FIF.POWER_BUTTON,
            ["开机自启动  ", "自动更新"],
            "开机后自动在后台运行zb小程序",
            self.personalGroup
        )
        self.linkCard = pushSettingCard(
            ["桌面", "开始菜单"],
            FIF.ADD_TO,
            "添加快捷方式",
            "添加程序的快捷方式至您的计算机中",
            self.personalGroup
        )

        self.aboutGroup = SettingCardGroup("关于", self.scrollWidget)
        self.helpCard = linkCard(
            [program_url, "start NotePad.exe " + join(user_path, "zb/zb.log"), abs_path],
            ["打开程序官网", "查看运行日志", "打开安装目录"],
            FIF.HELP,
            "帮助",
            "帮助您解决" + program_name + "的相关问题",
            self.aboutGroup
        )
        self.aboutCard = updateSettingCard(
            "检查更新",
            FIF.INFO,
            "关于",
            "By " + zb_name + " 2022-2023\n版本 " + version,
            self.aboutGroup,
            self,
        )
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.checkBoxCard)
        self.personalGroup.addSettingCard(self.linkCard)

        self.aboutGroup.addSettingCard(self.helpCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.aboutGroup)
        self.themeColorCard.colorChanged.connect(setThemeColor)
        # 属性设置
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 0)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName("设置")

        self.scrollWidget.setObjectName("scrollWidget")
        self.settingLabel.setObjectName("settingLabel")
        StyleSheet.SETTING_INTERFACE.apply(self)

        self.settingLabel.move(36, 30)