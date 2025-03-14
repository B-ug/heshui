"""统计功能测试模块。"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# 在导入 WeeklyStatsWidget 之前先模拟 matplotlib
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端进行测试

from heshui.models import DatabaseManager
from heshui.stats import WeeklyStatsWidget


@pytest.fixture
def mock_db():
    """模拟数据库管理器。"""
    with patch('heshui.stats.DatabaseManager') as mock:
        db_instance = MagicMock()
        mock.return_value = db_instance
        
        # 模拟周数据
        today = datetime.now().date()
        weekly_data = []
        
        # 生成过去7天的模拟数据
        for i in range(7):
            day = today - timedelta(days=6-i)
            day_str = day.strftime('%m-%d')
            # 生成一些随机数据，这里简单使用日期的天数作为数据
            amount = (day.day * 100) % 2000 + 500
            weekly_data.append((day_str, amount))
        
        db_instance.get_weekly_data.return_value = weekly_data
        yield db_instance


def test_weekly_stats_widget_creation(qtbot, mock_db):
    """测试周统计视图创建。"""
    widget = WeeklyStatsWidget()
    qtbot.addWidget(widget)
    
    # 验证数据库方法被调用
    mock_db.get_weekly_data.assert_called_once()
    
    # 验证界面元素存在
    assert hasattr(widget, 'chart_canvas')
    assert widget.chart_canvas is not None


def test_weekly_stats_update_chart(qtbot, mock_db):
    """测试更新图表功能。"""
    widget = WeeklyStatsWidget()
    qtbot.addWidget(widget)
    
    # 重置模拟对象的调用计数
    mock_db.get_weekly_data.reset_mock()
    
    # 调用更新方法
    widget.updateChart()
    
    # 验证数据库方法被再次调用
    mock_db.get_weekly_data.assert_called_once() 