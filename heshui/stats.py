"""统计视图模块。

提供饮水数据的统计图表功能。
"""
from typing import List, Tuple
import traceback
import sys
from datetime import datetime, timedelta

try:
    import matplotlib
    # 在导入其他 matplotlib 模块之前设置后端
    matplotlib.use('QtAgg')  # 使用通用的 QtAgg 后端，它会自动选择合适的 Qt 版本
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
except ImportError as e:
    print(f"导入 matplotlib 时出错: {e}")
    traceback.print_exc()

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                           QHBoxLayout, QPushButton, QDateEdit,
                           QTabWidget)

from heshui.models import DatabaseManager


class MatplotlibCanvas(FigureCanvasQTAgg):
    """Matplotlib画布类，用于在Qt界面中嵌入matplotlib图表。"""
    
    def __init__(self, width: int = 5, height: int = 4, dpi: int = 100):
        """初始化画布。
        
        Args:
            width: 图表宽度（英寸）
            height: 图表高度（英寸）
            dpi: 分辨率（每英寸点数）
        """
        try:
            self.fig = Figure(figsize=(width, height), dpi=dpi)
            self.axes = self.fig.add_subplot(111)
            super().__init__(self.fig)
            
            # 设置中文字体支持
            try:
                plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'sans-serif']  # 尝试多种中文字体
                plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
            except Exception as e:
                print(f"设置中文字体支持时出错: {e}")
        except Exception as e:
            print(f"初始化 MatplotlibCanvas 时出错: {e}")
            traceback.print_exc()
            raise


class WeeklyStatsWidget(QWidget):
    """周饮水量统计视图类。"""
    
    def __init__(self, parent=None):
        """初始化统计视图。
        
        Args:
            parent: 父窗口
        """
        try:
            super().__init__(parent)
            self.db = DatabaseManager()
            self.initUI()
            self.updateChart()
        except Exception as e:
            print(f"初始化 WeeklyStatsWidget 时出错: {e}")
            traceback.print_exc()
            raise
    
    def initUI(self) -> None:
        """初始化用户界面。"""
        try:
            layout = QVBoxLayout(self)
            
            # 标题
            title_label = QLabel("本周饮水量统计")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_font = title_label.font()
            title_font.setPointSize(14)
            title_font.setBold(True)
            title_label.setFont(title_font)
            layout.addWidget(title_label)
            
            # 图表
            try:
                self.chart_canvas = MatplotlibCanvas(width=6, height=4)
                layout.addWidget(self.chart_canvas)
            except Exception as e:
                print(f"创建图表画布时出错: {e}")
                error_label = QLabel(f"无法创建图表: {str(e)}")
                error_label.setWordWrap(True)
                error_label.setStyleSheet("color: red;")
                layout.addWidget(error_label)
            
            # 刷新按钮
            button_layout = QHBoxLayout()
            refresh_btn = QPushButton("刷新数据")
            refresh_btn.clicked.connect(self.updateChart)
            button_layout.addStretch()
            button_layout.addWidget(refresh_btn)
            layout.addLayout(button_layout)
            
            # 添加一些底部空间
            layout.addStretch()
        except Exception as e:
            print(f"初始化 WeeklyStatsWidget UI 时出错: {e}")
            traceback.print_exc()
    
    def updateChart(self) -> None:
        """更新图表数据。"""
        if not hasattr(self, 'chart_canvas'):
            print("图表画布不存在，无法更新图表")
            return
            
        try:
            # 获取周数据
            weekly_data = self.db.get_weekly_data()
            
            # 清除当前图表
            self.chart_canvas.axes.clear()
            
            # 准备数据
            dates = [item[0] for item in weekly_data]
            amounts = [item[1] for item in weekly_data]
            
            # 绘制曲线图
            self.chart_canvas.axes.plot(
                dates, 
                amounts, 
                marker='o',  # 添加圆形标记点
                linestyle='-',  # 实线
                linewidth=2,  # 线宽
                color='#2196F3',  # 使用应用主题色
                markersize=8  # 标记点大小
            )
            
            # 为每个数据点添加数值标注
            for i, (date, amount) in enumerate(zip(dates, amounts)):
                self.chart_canvas.axes.annotate(
                    f"{amount}ml",  # 显示的文本
                    (date, amount),  # 标注位置
                    textcoords="offset points",  # 使用偏移坐标
                    xytext=(0, 10),  # 文本偏移量（上方10个点）
                    ha='center',  # 水平居中对齐
                    fontsize=9,  # 字体大小
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8)  # 添加文本框
                )
            
            # 填充曲线下方区域
            self.chart_canvas.axes.fill_between(
                dates, 
                amounts, 
                alpha=0.2,  # 透明度
                color='#2196F3'  # 使用应用主题色
            )
            
            # 设置图表标题和标签
            self.chart_canvas.axes.set_title("每日饮水量趋势")
            self.chart_canvas.axes.set_xlabel("日期")
            self.chart_canvas.axes.set_ylabel("饮水量 (ml)")
            
            # 设置网格线
            self.chart_canvas.axes.grid(True, linestyle='--', alpha=0.7)
            
            # 获取每日目标
            from heshui.config import Config
            daily_goal = Config().get('daily_goal')
            
            # 添加目标线
            self.chart_canvas.axes.axhline(
                y=daily_goal, 
                color='r', 
                linestyle='--', 
                alpha=0.7,
                label=f"目标 ({daily_goal}ml)"
            )
            
            # 添加图例
            self.chart_canvas.axes.legend()
            
            # 自动调整布局
            self.chart_canvas.fig.tight_layout()
            
            # 刷新画布
            self.chart_canvas.draw()
            
        except Exception as e:
            print(f"更新图表时出错: {e}")
            traceback.print_exc()
            # 显示错误信息
            try:
                self.chart_canvas.axes.clear()
                self.chart_canvas.axes.text(
                    0.5, 0.5, 
                    f"加载数据时出错:\n{str(e)}", 
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=self.chart_canvas.axes.transAxes
                )
                self.chart_canvas.draw()
            except Exception as inner_e:
                print(f"显示错误信息时出错: {inner_e}")
                traceback.print_exc() 


class DailyStatsWidget(QWidget):
    """日饮水量统计视图类。"""
    
    def __init__(self, parent=None):
        """初始化日统计视图。
        
        Args:
            parent: 父窗口
        """
        try:
            super().__init__(parent)
            self.db = DatabaseManager()
            self.selected_date = datetime.now()
            self.initUI()
            self.updateChart()
        except Exception as e:
            print(f"初始化 DailyStatsWidget 时出错: {e}")
            traceback.print_exc()
            raise
    
    def initUI(self) -> None:
        """初始化用户界面。"""
        try:
            layout = QVBoxLayout(self)
            
            # 标题
            title_label = QLabel("每日饮水量详情")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_font = title_label.font()
            title_font.setPointSize(14)
            title_font.setBold(True)
            title_label.setFont(title_font)
            layout.addWidget(title_label)
            
            # 日期选择器
            date_layout = QHBoxLayout()
            date_label = QLabel("选择日期:")
            self.date_edit = QDateEdit()
            self.date_edit.setCalendarPopup(True)  # 允许弹出日历选择
            self.date_edit.setDate(QDate.currentDate())  # 默认为当前日期
            self.date_edit.dateChanged.connect(self.onDateChanged)
            
            date_layout.addWidget(date_label)
            date_layout.addWidget(self.date_edit)
            date_layout.addStretch()
            layout.addLayout(date_layout)
            
            # 图表
            try:
                self.chart_canvas = MatplotlibCanvas(width=6, height=4)
                layout.addWidget(self.chart_canvas)
            except Exception as e:
                print(f"创建图表画布时出错: {e}")
                error_label = QLabel(f"无法创建图表: {str(e)}")
                error_label.setWordWrap(True)
                error_label.setStyleSheet("color: red;")
                layout.addWidget(error_label)
            
            # 刷新按钮
            button_layout = QHBoxLayout()
            refresh_btn = QPushButton("刷新数据")
            refresh_btn.clicked.connect(self.updateChart)
            button_layout.addStretch()
            button_layout.addWidget(refresh_btn)
            layout.addLayout(button_layout)
            
            # 添加一些底部空间
            layout.addStretch()
        except Exception as e:
            print(f"初始化 DailyStatsWidget UI 时出错: {e}")
            traceback.print_exc()
    
    def onDateChanged(self, qdate: QDate) -> None:
        """日期改变时的处理函数。
        
        Args:
            qdate: 新选择的日期
        """
        try:
            # 将 QDate 转换为 datetime
            self.selected_date = datetime(qdate.year(), qdate.month(), qdate.day())
            self.updateChart()
        except Exception as e:
            print(f"处理日期变更时出错: {e}")
            traceback.print_exc()
    
    def updateChart(self) -> None:
        """更新图表数据。"""
        if not hasattr(self, 'chart_canvas'):
            print("图表画布不存在，无法更新图表")
            return
            
        try:
            # 获取日数据
            daily_data = self.db.get_day_records(self.selected_date)
            
            # 清除当前图表
            self.chart_canvas.axes.clear()
            
            # 准备数据
            hours = [item[0] for item in daily_data]
            amounts = [item[1] for item in daily_data]
            
            # 绘制曲线图
            self.chart_canvas.axes.plot(
                hours, 
                amounts, 
                marker='o',  # 添加圆形标记点
                linestyle='-',  # 实线
                linewidth=2,  # 线宽
                color='#2196F3',  # 使用应用主题色
                markersize=6  # 标记点大小
            )
            
            # 为非零数据点添加数值标注
            for i, (hour, amount) in enumerate(zip(hours, amounts)):
                if amount > 0:  # 只为有饮水记录的时间点添加标注
                    self.chart_canvas.axes.annotate(
                        f"{amount}ml",  # 显示的文本
                        (hour, amount),  # 标注位置
                        textcoords="offset points",  # 使用偏移坐标
                        xytext=(0, 10),  # 文本偏移量（上方10个点）
                        ha='center',  # 水平居中对齐
                        fontsize=9,  # 字体大小
                        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8)  # 添加文本框
                    )
            
            # 填充曲线下方区域
            self.chart_canvas.axes.fill_between(
                hours, 
                amounts, 
                alpha=0.2,  # 透明度
                color='#2196F3'  # 使用应用主题色
            )
            
            # 设置图表标题和标签
            date_str = self.selected_date.strftime('%Y-%m-%d')
            self.chart_canvas.axes.set_title(f"{date_str} 饮水量分布")
            self.chart_canvas.axes.set_xlabel("时间")
            self.chart_canvas.axes.set_ylabel("饮水量 (ml)")
            
            # 设置网格线
            self.chart_canvas.axes.grid(True, linestyle='--', alpha=0.7)
            
            # 设置x轴刻度，每3小时显示一个
            self.chart_canvas.axes.set_xticks([hours[i] for i in range(0, 24, 3)])
            
            # 自动调整布局
            self.chart_canvas.fig.tight_layout()
            
            # 刷新画布
            self.chart_canvas.draw()
            
        except Exception as e:
            print(f"更新日图表时出错: {e}")
            traceback.print_exc()
            # 显示错误信息
            try:
                self.chart_canvas.axes.clear()
                self.chart_canvas.axes.text(
                    0.5, 0.5, 
                    f"加载数据时出错:\n{str(e)}", 
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=self.chart_canvas.axes.transAxes
                )
                self.chart_canvas.draw()
            except Exception as inner_e:
                print(f"显示错误信息时出错: {inner_e}")
                traceback.print_exc()


class StatsTabWidget(QTabWidget):
    """统计图表标签页组件。"""
    
    def __init__(self, parent=None):
        """初始化统计标签页。
        
        Args:
            parent: 父窗口
        """
        try:
            super().__init__(parent)
            self.initUI()
        except Exception as e:
            print(f"初始化 StatsTabWidget 时出错: {e}")
            traceback.print_exc()
            raise
    
    def initUI(self) -> None:
        """初始化用户界面。"""
        try:
            # 添加周视图标签页
            weekly_tab = WeeklyStatsWidget(self)
            self.addTab(weekly_tab, "周视图")
            
            # 添加日视图标签页
            daily_tab = DailyStatsWidget(self)
            self.addTab(daily_tab, "日视图")
            
            # 设置默认显示的标签页
            self.setCurrentIndex(0)
        except Exception as e:
            print(f"初始化 StatsTabWidget UI 时出错: {e}")
            traceback.print_exc() 