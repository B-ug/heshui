"""
打包脚本，用于将应用程序打包成可执行文件。
"""
import PyInstaller.__main__
import os
from pathlib import Path

def main():
    """
    主打包函数。
    """
    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent.absolute()
    
    # 设置图标路径
    icon_path = current_dir / 'heshui' / 'resources' / 'icons' / 'drink.ico'
    
    # 设置打包参数
    params = [
        'run.py',  # 主程序文件
        '--name=喝水提醒',  # 可执行文件名称
        '--noconsole',  # 不显示控制台窗口
        f'--icon={icon_path}',  # 设置应用图标
        '--noconfirm',  # 覆盖输出目录
        '--clean',  # 清理临时文件
        '--add-data=heshui/resources/icons;heshui/resources/icons',  # 添加资源文件
        '--hidden-import=PyQt6.QtSvg',  # 添加必要的隐藏导入
        '--hidden-import=PyQt6.QtSvgWidgets',
        '--onefile',  # 打包成单个文件
    ]
    
    # 执行打包
    PyInstaller.__main__.run(params)

if __name__ == '__main__':
    main() 