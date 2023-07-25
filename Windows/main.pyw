from view.main_window import *
from common.resource import *

saveSetting(abs_cache, os.getpid())

QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
translator = FluentTranslator(QLocale())
app.installTranslator(translator)
w = MainWindow()
w.show()
if ":\WINDOWS\system32".lower() in old_path.lower():
    w.hide()
app.exec_()
