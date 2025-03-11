"""喝水提醒应用程序主模块。

包含主窗口和系统托盘的实现。
"""
import sys
from datetime import datetime, timedelta
from typing import Optional
import os
from pathlib import Path

from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPainter, QAction, QConicalGradient, QColor, QPen
from PyQt6.QtWidgets import (QApplication, QMainWindow, QMenu, QSystemTrayIcon,
                           QWidget, QVBoxLayout, QPushButton, QLabel,
                           QProgressBar, QMessageBox, QHBoxLayout)

from heshui.config import Config
from heshui.models import DatabaseManager
from heshui.settings import SettingsDialog


class CircularProgress(QWidget):
    """环形进度条控件。
    
    一个美观的圆环形进度条，使用蓝色渐变效果。
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.value = 0
        self.setMinimumSize(200, 200)
        
        # 设置渐变色
        self.gradient = self._create_gradient()
        
        # 进度条样式参数
        self.ring_width = 12  # 圆环宽度调整得更细一些
        self.start_angle = 90  # 起始角度（12点钟方向）
        
        # 设置主题色
        self.theme_color = QColor(33, 150, 243)  # 设置统一的主题色
    
    def _create_gradient(self) -> 'QConicalGradient':
        """创建圆锥渐变。"""
        gradient = QConicalGradient(0.5, 0.5, 90)
        gradient.setCoordinateMode(gradient.CoordinateMode.ObjectBoundingMode)
        
        # 使用更多的渐变点来实现更平滑的过渡
        # 使用更多的中间点，让渐变更加平滑
        for i in range(11):  # 0到1之间创建11个点
            pos = i / 10
            # 使用正弦函数创建更平滑的渐变
            import math
            t = math.sin(pos * math.pi / 2)  # 使用正弦函数使过渡更自然
            
            # 计算颜色
            r = int(179 + (33 - 179) * t)  # 从浅蓝到主题蓝
            g = int(229 + (150 - 229) * t)
            b = int(252 + (243 - 252) * t)
            
            gradient.setColorAt(pos, QColor(r, g, b))
        
        return gradient
    
    def setValue(self, value: float) -> None:
        """设置进度值（0-100）。"""
        self.value = max(0, min(value, 100))
        self.update()
    
    def paintEvent(self, event) -> None:
        """绘制环形进度条。"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 计算绘制区域
        side = min(self.width(), self.height())
        rect = self.rect().adjusted(
            self.ring_width, 
            self.ring_width, 
            -self.ring_width, 
            -self.ring_width
        )
        
        # 绘制背景圆环
        background_pen = QPen()
        background_pen.setWidth(self.ring_width)
        background_pen.setColor(QColor(238, 238, 238))  # 使用更浅的灰色
        background_pen.setCapStyle(Qt.PenCapStyle.RoundCap)  # 背景也使用圆形线帽
        painter.setPen(background_pen)
        painter.drawEllipse(rect)
        
        # 如果有进度，绘制进度圆环
        if self.value > 0:
            # 设置渐变画笔
            gradient_pen = QPen()
            gradient_pen.setWidth(self.ring_width)
            gradient_pen.setBrush(self.gradient)
            gradient_pen.setCapStyle(Qt.PenCapStyle.RoundCap)  # 添加圆形线帽
            painter.setPen(gradient_pen)
            
            # 计算角度
            span_angle = int(-self.value * 360 / 100)
            
            # 绘制进度圆环
            painter.drawArc(rect, self.start_angle * 16, span_angle * 16)
        
        # 绘制中心文字
        painter.setPen(self.theme_color)  # 使用主题色绘制文字
        
        # 准备文本
        number_text = f"{int(self.value)}"
        
        # 设置数字字体
        number_font = painter.font()
        number_font.setPixelSize(side // 3)  # 调整数字大小
        number_font.setBold(True)  # 设置为粗体
        painter.setFont(number_font)
        
        # 计算数字宽度
        metrics = painter.fontMetrics()
        number_width = metrics.horizontalAdvance(number_text)
        
        # 设置百分号字体
        percent_font = painter.font()
        percent_font.setPixelSize(side // 8)  # 百分号字体小一些
        
        # 计算百分号宽度
        painter.setFont(percent_font)
        percent_width = painter.fontMetrics().horizontalAdvance("%")
        
        # 计算总宽度和起始位置
        total_width = number_width + percent_width + side // 20  # 添加一些间距
        start_x = (side - total_width) // 2
        
        # 绘制数字
        painter.setFont(number_font)
        number_rect = rect.adjusted(0, 0, 0, 0)
        number_rect.moveLeft(start_x)
        painter.drawText(number_rect, int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter), number_text)
        
        # 绘制百分号
        painter.setFont(percent_font)
        percent_rect = rect.adjusted(0, side//8, 0, 0)  # 稍微向下调整
        percent_rect.moveLeft(start_x + number_width + side//20)  # 添加间距
        painter.drawText(percent_rect, int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter), "%")

class MainWindow(QMainWindow):
    """主窗口类。"""
    
    drink_recorded = pyqtSignal()  # 记录饮水信号
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.db = DatabaseManager()
        self.initUI()
        self.setupSystemTray()
        self.setupTimer()
        
        # 设置应用程序图标
        icon_path = Path(__file__).parent / 'resources' / 'icons' / 'drink.ico'
        self.setWindowIcon(QIcon(str(icon_path)))
    
    def initUI(self) -> None:
        """初始化用户界面。"""
        self.setWindowTitle('喝水提醒')
        self.setMinimumSize(300, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)  # 设置边距
        
        # 创建顶部工具栏布局
        top_bar = QHBoxLayout()
        top_bar.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # 创建设置按钮
        settings_btn = QPushButton()
        settings_btn.setFixedSize(32, 32)  # 设置固定大小
        settings_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 16px;
            }
        """)
        # 使用 SVG 图标
        icon_path = Path(__file__).parent / 'resources' / 'icons' / 'settings.svg'
        settings_btn.setIcon(QIcon(str(icon_path)))
        settings_btn.setIconSize(QSize(20, 20))  # 设置图标大小
        settings_btn.clicked.connect(self.showSettings)
        top_bar.addWidget(settings_btn)
        
        layout.addLayout(top_bar)
        
        # 进度显示
        self.progress = CircularProgress()
        layout.addWidget(self.progress, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 状态标签
        self.status_label = QLabel()
        layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 下次提醒时间
        self.next_reminder_label = QLabel()
        layout.addWidget(self.next_reminder_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 操作按钮
        drink_btn = QPushButton('记录饮水')
        drink_btn.clicked.connect(self.recordDrink)
        layout.addWidget(drink_btn)
        
        self.updateStatus()
    
    def setupSystemTray(self) -> None:
        """设置系统托盘。"""
        self.tray_icon = QSystemTrayIcon(self)
        # 使用文件系统中的图标
        icon_path = Path(__file__).parent / 'resources' / 'icons' / 'drink.ico'
        self.tray_icon.setIcon(QIcon(str(icon_path)))
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        show_action = QAction('显示主窗口', self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        self.mute_action = QAction('静音提醒', self)
        self.mute_action.setCheckable(True)
        self.mute_action.setChecked(self.config.get('mute'))
        self.mute_action.triggered.connect(self.toggleMute)
        tray_menu.addAction(self.mute_action)
        
        tray_menu.addSeparator()
        quit_action = QAction('退出', self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # 连接托盘图标的点击事件
        self.tray_icon.activated.connect(self.onTrayIconActivated)
    
    def setupTimer(self) -> None:
        """设置定时器。"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showReminder)
        self.resetTimer()
    
    def resetTimer(self) -> None:
        """重置定时器。"""
        interval = self.config.get('reminder_interval') * 60 * 1000  # 转换为毫秒
        self.timer.start(interval)
        self.updateNextReminderTime()
    
    def updateNextReminderTime(self) -> None:
        """更新下次提醒时间显示。"""
        next_time = datetime.now() + timedelta(minutes=self.config.get('reminder_interval'))
        self.next_reminder_label.setText(f'下次提醒: {next_time.strftime("%H:%M")}')
    
    def updateStatus(self) -> None:
        """更新状态显示。"""
        total = self.db.get_total_today()
        goal = self.config.get('daily_goal')
        progress = min(100, total * 100 / goal)
        
        self.progress.setValue(progress)
        self.status_label.setText(f'今日已饮水: {total}ml / {goal}ml')
    
    def recordDrink(self) -> None:
        """记录饮水。"""
        amount = 200  # 默认饮水量
        self.db.add_record(amount)
        self.updateStatus()
        self.resetTimer()
        self.drink_recorded.emit()
        
        # 显示成功提示
        self.tray_icon.showMessage(
            '记录成功',
            f'已记录饮水 {amount}ml',
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
    
    def showReminder(self) -> None:
        """显示提醒。"""
        if not self.config.get('mute'):
            self.tray_icon.showMessage(
                '喝水提醒',
                self.config.get('reminder_text'),
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )
    
    def toggleMute(self, checked: bool) -> None:
        """切换静音状态。"""
        self.config.set('mute', checked)
    
    def showSettings(self) -> None:
        """显示设置对话框。"""
        dialog = SettingsDialog(self)
        if dialog.exec() == SettingsDialog.DialogCode.Accepted:  # 注意这里的改动
            # 更新UI显示
            self.updateStatus()
            self.resetTimer()
            # 更新托盘菜单的静音状态
            self.mute_action.setChecked(self.config.get('mute'))
    
    def onTrayIconActivated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """处理托盘图标的激活事件。"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # 单击
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()
    
    def closeEvent(self, event) -> None:
        """处理窗口关闭事件。"""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            '喝水提醒',
            '应用程序已最小化到系统托盘',
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )

def main():
    """应用程序入口函数。"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    window = MainWindow()
    if not Config().get('start_minimized'):
        window.show()
    
    sys.exit(app.exec()) 