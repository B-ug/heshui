"""设置对话框模块。

提供应用程序设置界面。
"""
from typing import Dict, Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                           QSpinBox, QLineEdit, QCheckBox, QPushButton)

from heshui.config import Config

class SettingsDialog(QDialog):
    """设置对话框类。"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = Config()
        self.initUI()
        self.loadSettings()
    
    def initUI(self) -> None:
        """初始化用户界面。"""
        self.setWindowTitle('设置')
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        
        # 提醒间隔设置
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel('提醒间隔(分钟):'))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 240)
        interval_layout.addWidget(self.interval_spin)
        layout.addLayout(interval_layout)
        
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
        self.interval_spin.setValue(settings['reminder_interval'])
        self.goal_spin.setValue(settings['daily_goal'])
        self.text_edit.setText(settings['reminder_text'])
        self.mute_check.setChecked(settings['mute'])
        self.minimize_check.setChecked(settings['start_minimized'])
    
    def saveSettings(self) -> None:
        """保存设置。"""
        settings = {
            'reminder_interval': self.interval_spin.value(),
            'daily_goal': self.goal_spin.value(),
            'reminder_text': self.text_edit.text(),
            'mute': self.mute_check.isChecked(),
            'start_minimized': self.minimize_check.isChecked()
        }
        
        for key, value in settings.items():
            self.config.set(key, value)
        
        self.accept() 