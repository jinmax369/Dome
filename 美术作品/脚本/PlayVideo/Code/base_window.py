import os
import sys
from pathlib import Path
from typing import Optional
from PySide6.QtCore import QFile,Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout



class MainWindow(QWidget):
    """主窗口类，负责加载和管理UI界面"""

    def __init__(self,parent = None):
        super().__init__(parent)

        # 获取脚本运行目录
        self.script_path =""
        self.script_name =""
        self.ui = None

        # 查找并加载UI文件
        # self.load_ui()

    def load_ui(self) -> None:
        """加载UI文件"""
        # 获取当前脚本文件名（不带扩展名）
        # script_name = Path(__file__).stem
        # 构造UI文件路径（与脚本文件同名，扩展名为.ui）
        ui_file_name = f"{self.script_name}.ui"
        ui_file_path = os.path.join(self.script_path,"Ui", ui_file_name)

        # 检查UI文件是否存在
        if not os.path.exists(ui_file_path):
            raise FileNotFoundError(f"UI文件未找到: {ui_file_path}")

        # 加载UI文件
        loader = QUiLoader()
        ui_file = QFile(str(ui_file_path))

        if not ui_file.open(QFile.ReadOnly):
            raise IOError(f"无法打开UI文件: {ui_file_path}")

        try:
            self.ui = loader.load(ui_file, self)
            # self.ui.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.ui.setParent(self)

            # 创建布局并添加UI组件
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.ui)
            self.setLayout(layout)

        finally:
            ui_file.close()


# def main() -> None:
#     """应用程序主入口"""
#     app = QApplication.instance() or QApplication(sys.argv)

#     try:
#         # 创建并显示主窗口
#         window = MainWindow()
#         #窗口置顶
#         window.setWindowFlags(window.windowFlags() | Qt.WindowStaysOnTopHint)
#         window.show()

#         # 如果运行在Unreal环境中，将窗口嵌入到Unreal编辑器
#         if hasattr(unreal, 'parent_external_window_to_slate'):
#             unreal.parent_external_window_to_slate(window.winId())

#         # 启动应用程序事件循环
#         sys.exit(app.exec())

#     except Exception as e:
#         print(f"程序启动失败: {e}")
#         if hasattr(unreal, 'log_error'):
#             unreal.log_error(f"Python脚本启动失败: {e}")
#         sys.exit(1)


# if __name__ == '__main__':
#     main()