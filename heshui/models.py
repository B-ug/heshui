"""数据模型定义模块。

包含所有与数据库相关的模型类定义。
"""
from datetime import datetime, timedelta, time
from typing import Optional, Dict, List, Tuple
import sqlite3

from sqlalchemy import Column, DateTime, Integer, String, Time, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

Base = declarative_base()

class DrinkRecord(Base):
    """饮水记录模型类。
    
    Attributes:
        id (int): 记录ID
        timestamp (datetime): 记录时间
        amount (int): 饮水量(ml)
        note (str): 备注信息
    """
    
    __tablename__ = 'drink_records'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
    amount = Column(Integer, nullable=False)
    note = Column(String(200))

class ReminderTime(Base):
    """提醒时间点模型类。
    
    Attributes:
        id (int): 记录ID
        time (time): 提醒时间
    """
    
    __tablename__ = 'reminder_times'
    
    id = Column(Integer, primary_key=True)
    time = Column(Time, nullable=False, unique=True)

class DatabaseManager:
    """数据库管理类。
    
    负责处理所有数据库操作的单例类。
    """
    
    _instance: Optional['DatabaseManager'] = None
    
    def __new__(cls) -> 'DatabaseManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """初始化数据库连接和会话。"""
        self.engine = create_engine('sqlite:///drink_records.db')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # 如果没有设置提醒时间点，添加默认时间点
        self._add_default_reminder_times_if_empty()
    
    def _add_default_reminder_times_if_empty(self) -> None:
        """如果没有设置提醒时间点，添加默认时间点。"""
        with self.Session() as session:
            count = session.query(ReminderTime).count()
            if count == 0:
                # 添加默认的提醒时间点：9:00, 12:00, 15:00, 18:00
                default_times = [time(9, 0), time(12, 0), time(15, 0), time(18, 0)]
                for t in default_times:
                    session.add(ReminderTime(time=t))
                session.commit()
    
    def add_record(self, amount: int, note: str = "") -> None:
        """添加新的饮水记录。
        
        Args:
            amount: 饮水量(ml)
            note: 可选的备注信息
        """
        with self.Session() as session:
            record = DrinkRecord(amount=amount, note=note)
            session.add(record)
            session.commit()
    
    def get_today_records(self) -> list[DrinkRecord]:
        """获取今天的所有饮水记录。
        
        Returns:
            list[DrinkRecord]: 今天的饮水记录列表
        """
        today = datetime.now().date()
        with self.Session() as session:
            return session.query(DrinkRecord).filter(
                DrinkRecord.timestamp >= today
            ).all()
    
    def get_total_today(self) -> int:
        """获取今日总饮水量。
        
        Returns:
            int: 总饮水量(ml)
        """
        records = self.get_today_records()
        return sum(record.amount for record in records)
        
    def get_weekly_data(self) -> List[Tuple[str, int]]:
        """获取过去一周的每日饮水量数据。
        
        Returns:
            List[Tuple[str, int]]: 包含日期和饮水量的元组列表，格式为 [(日期字符串, 饮水量), ...]
        """
        try:
            # 计算过去7天的日期范围
            today = datetime.now().date()
            start_date = today - timedelta(days=6)  # 包括今天在内的7天
            
            # 使用原生SQL查询按日期分组统计
            # SQLAlchemy的分组查询在这里较为复杂，使用原生SQL更直观
            conn = sqlite3.connect('drink_records.db')
            cursor = conn.cursor()
            
            # 准备查询，按日期分组获取每天的总饮水量
            query = """
            SELECT date(timestamp) as day, SUM(amount) as total
            FROM drink_records
            WHERE date(timestamp) >= ?
            GROUP BY day
            ORDER BY day
            """
            
            cursor.execute(query, (start_date.isoformat(),))
            results = cursor.fetchall()
            conn.close()
            
            # 确保所有7天都有数据，没有记录的日期设为0
            date_dict = {(start_date + timedelta(days=i)).strftime('%m-%d'): 0 for i in range(7)}
            
            # 更新有记录的日期
            for day_str, amount in results:
                # 将日期格式从 YYYY-MM-DD 转换为 MM-DD
                day = datetime.strptime(day_str, '%Y-%m-%d').strftime('%m-%d')
                date_dict[day] = amount
            
            # 转换为有序列表
            return [(day, amount) for day, amount in date_dict.items()]
            
        except Exception as e:
            print(f"获取周数据时出错: {e}")
            return [(datetime.now().strftime('%m-%d'), 0)]  # 返回空数据 
    
    def get_reminder_times(self) -> List[time]:
        """获取所有提醒时间点。
        
        Returns:
            List[time]: 提醒时间点列表，按时间排序
        """
        with self.Session() as session:
            times = session.query(ReminderTime).order_by(ReminderTime.time).all()
            return [t.time for t in times]
    
    def add_reminder_time(self, reminder_time: time) -> bool:
        """添加新的提醒时间点。
        
        Args:
            reminder_time: 提醒时间
            
        Returns:
            bool: 是否添加成功
        """
        try:
            with self.Session() as session:
                # 检查是否已存在相同时间点
                existing = session.query(ReminderTime).filter(
                    ReminderTime.time == reminder_time
                ).first()
                
                if existing:
                    return False  # 已存在相同时间点
                
                session.add(ReminderTime(time=reminder_time))
                session.commit()
                return True
        except Exception as e:
            print(f"添加提醒时间点时出错: {e}")
            return False
    
    def delete_reminder_time(self, reminder_time: time) -> bool:
        """删除提醒时间点。
        
        Args:
            reminder_time: 要删除的提醒时间
            
        Returns:
            bool: 是否删除成功
        """
        try:
            with self.Session() as session:
                time_obj = session.query(ReminderTime).filter(
                    ReminderTime.time == reminder_time
                ).first()
                
                if not time_obj:
                    return False
                
                session.delete(time_obj)
                session.commit()
                return True
        except Exception as e:
            print(f"删除提醒时间点时出错: {e}")
            return False 