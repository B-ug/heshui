"""设置对话框模块。

提供应用程序设置界面。
"""
from datetime import time
from typing import Dict, Any, List
import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                           QSpinBox, QLineEdit, QCheckBox, QPushButton,
                           QListWidget, QTimeEdit, QMessageBox, QListWidgetItem)

try:
    import win32api
    import win32con
    HAS_WIN32API = True
except ImportError:
    HAS_WIN32API = False

from heshui.config import Config
from heshui.models import DatabaseManager

class SettingsDialog(QDialog):
    """设置对话框类。"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = Config()
        self.db = DatabaseManager()
        self.reminder_times = self.db.get_reminder_times()
        self.initUI()
        self.loadSettings()
    
    def initUI(self) -> None:
        """初始化用户界面。"""
        self.setWindowTitle('设置')
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # 提醒时间点设置
        time_layout = QVBoxLayout()
        time_layout.addWidget(QLabel('提醒时间点:'))
        
        # 时间点列表
        self.time_list = QListWidget()
        self.time_list.setMinimumHeight(150)
        time_layout.addWidget(self.time_list)
        
        # 添加时间点控件
        add_time_layout = QHBoxLayout()
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        add_time_layout.addWidget(self.time_edit)
        
        add_btn = QPushButton('添加')
        add_btn.clicked.connect(self.addReminderTime)
        add_time_layout.addWidget(add_btn)
        
        delete_btn = QPushButton('删除')
        delete_btn.clicked.connect(self.deleteReminderTime)
        add_time_layout.addWidget(delete_btn)
        
        time_layout.addLayout(add_time_layout)
        layout.addLayout(time_layout)
        
        # 每日目标设置
        goal_layout = QHBoxLayout()
        goal_layout.addWidget(QLabel('每日目标(ml):'))
        self.goal_spin = QSpinBox()
        self.goal_spin.setRange(500, 5000)
        self.goal_spin.setSingleStep(100)
        goal_layout.addWidget(self.goal_spin)
        layout.addLayout(goal_layout)
        
        # 提醒文本设置
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel('提醒文本:'))
        self.text_edit = QLineEdit()
        text_layout.addWidget(self.text_edit)
        layout.addLayout(text_layout)
        
        # 静音设置
        self.mute_check = QCheckBox('静音提醒')
        layout.addWidget(self.mute_check)
        
        # 启动时最小化设置
        self.minimize_check = QCheckBox('启动时最小化')
        layout.addWidget(self.minimize_check)
        
        # 开机自启动设置
        self.autostart_check = QCheckBox('开机自动启动')
        if not HAS_WIN32API:
            self.autostart_check.setEnabled(False)
            self.autostart_check.setToolTip('需要安装pywin32模块才能使用此功能')
        layout.addWidget(self.autostart_check)
        
        # 按钮
        button_layout = QHBoxLayout()
        save_btn = QPushButton('保存')
        save_btn.clicked.connect(self.saveSettings)
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
    
    def loadSettings(self) -> None:
        """加载当前设置。"""
        settings = self.config.get_all()
        self.goal_spin.setValue(settings['daily_goal'])
        self.text_edit.setText(settings['reminder_text'])
        self.mute_check.setChecked(settings['mute'])
        self.minimize_check.setChecked(settings['start_minimized'])
        
        # 加载开机自启动设置
        if HAS_WIN32API:
            self.autostart_check.setChecked(settings.get('autostart', False))
        
        # 加载提醒时间点
        self.updateTimeList()
    
    def updateTimeList(self) -> None:
        """更新时间点列表。"""
        self.time_list.clear()
        for t in sorted(self.reminder_times):
            self.time_list.addItem(t.strftime("%H:%M"))
    
    def addReminderTime(self) -> None:
        """添加新的提醒时间点。"""
        new_time = self.time_edit.time().toPyTime()
        
        # 检查是否已存在相同时间点
        if new_time in self.reminder_times:
            QMessageBox.warning(self, "添加失败", "该时间点已存在")
            return
        
        self.reminder_times.append(new_time)
        self.updateTimeList()
    
    def deleteReminderTime(self) -> None:
        """删除选中的提醒时间点。"""
        selected_items = self.time_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "删除失败", "请先选择要删除的时间点")
            return
        
        # 如果只剩下一个时间点，不允许删除
        if len(self.reminder_times) <= 1:
            QMessageBox.warning(self, "删除失败", "至少需要保留一个提醒时间点")
            return
        
        for item in selected_items:
            time_str = item.text()
            hour, minute = map(int, time_str.split(':'))
            time_obj = time(hour, minute)
            
            if time_obj in self.reminder_times:
                self.reminder_times.remove(time_obj)
        
        self.updateTimeList()
    
    def set_autostart(self, enable: bool) -> bool:
        """设置或取消开机自启动。
        
        Args:
            enable: 是否启用开机自启动
            
        Returns:
            bool: 操作是否成功
        """
        if not HAS_WIN32API:
            return False
            
        try:
            # 获取当前应用程序路径
            app_path = os.path.abspath(sys.argv[0])
            # 如果是 .py 文件，需要使用 pythonw 启动
            if app_path.endswith('.py'):
                app_path = f'pythonw "{app_path}"'
            # 如果是 .exe 文件，直接使用路径
            elif app_path.endswith('.exe'):
                app_path = f'"{app_path}"'
                
            # 打开注册表
            key = win32api.RegOpenKey(
                win32con.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Run',
                0, 
                win32con.KEY_SET_VALUE
            )
            
            app_name = "HeShuiApp"
            
            if enable:
                # 设置开机自启动
                win32api.RegSetValueEx(key, app_name, 0, win32con.REG_SZ, app_path)
            else:
                # 取消开机自启动
                try:
                    win32api.RegDeleteValue(key, app_name)
                except Exception:
                    # 如果键不存在，忽略错误
                    pass
                    
            win32api.RegCloseKey(key)
            return True
        except Exception as e:
            print(f"设置开机自启动失败: {e}")
            return False
    
    def saveSettings(self) -> None:
        """保存设置。"""
        settings = {
            'daily_goal': self.goal_spin.value(),
            'reminder_text': self.text_edit.text(),
            'mute': self.mute_check.isChecked(),
            'start_minimized': self.minimize_check.isChecked()
        }
        
        # 保存开机自启动设置
        if HAS_WIN32API:
            autostart = self.autostart_check.isChecked()
            settings['autostart'] = autostart
            self.set_autostart(autostart)
        
        for key, value in settings.items():
            self.config.set(key, value)
        
        # 保存提醒时间点
        # 先删除所有现有时间点
        current_times = self.db.get_reminder_times()
        for t in current_times:
            self.db.delete_reminder_time(t)
        
        # 添加新的时间点
        for t in self.reminder_times:
            self.db.add_reminder_time(t)
        
        self.accept() 