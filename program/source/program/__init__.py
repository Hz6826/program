from .program import *
from .setting import *

# 关闭SSL证书验证
import ssl

ssl._create_default_https_context = ssl._create_unverified_context()

# 日志设置
open(program.LOGGING_FILE_PATH, "w").close() if not f.existPath(program.LOGGING_FILE_PATH) or f.fileSize(program.LOGGING_FILE_PATH) >= 1024 * 128 else None

handler2 = logging.FileHandler(program.LOGGING_FILE_PATH)
handler2.setLevel(logging.DEBUG)
handler2.setFormatter(logging.Formatter("[%(levelname)s %(asctime)s %(filename)s %(process)s]:%(message)s"))

Log.addHandler(handler2)

Log.info(f"程序启动参数{program.STARTUP_ARGUMENT}!")

program.detectRepeatRun()

Log.info("程序动态数据api初始化成功！")
