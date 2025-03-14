#!/usr/bin/env python3
"""喝水提醒应用程序启动脚本。"""
import sys
import traceback

def excepthook(exc_type, exc_value, exc_traceback):
    """全局异常处理函数。"""
    print("发生未捕获的异常:")
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    from PyQt6.QtWidgets import QApplication, QMessageBox
    if QApplication.instance():
        QMessageBox.critical(
            None, 
            "错误", 
            f"程序发生错误: {exc_type.__name__}: {exc_value}\n\n"
            "请查看控制台输出获取详细信息。"
        )

# 设置全局异常处理器
sys.excepthook = excepthook

try:
    from heshui import main
    
    if __name__ == '__main__':
        main()
except ImportError as e:
    print(f"导入模块时出错: {e}")
    traceback.print_exc()
    from PyQt6.QtWidgets import QApplication, QMessageBox
    app = QApplication(sys.argv)
    QMessageBox.critical(
        None, 
        "导入错误", 
        f"无法启动应用程序: {str(e)}\n\n"
        "请确保已安装所有依赖并重新启动应用程序。"
    )
    sys.exit(1)
except Exception as e:
    print(f"启动应用程序时出错: {e}")
    traceback.print_exc()
    from PyQt6.QtWidgets import QApplication, QMessageBox
    app = QApplication(sys.argv)
    QMessageBox.critical(
        None, 
        "启动错误", 
        f"无法启动应用程序: {str(e)}\n\n"
        "请查看控制台输出获取详细信息。"
    )
    sys.exit(1) 