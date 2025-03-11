"""数据模型定义模块。

包含所有与数据库相关的模型类定义。
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, create_engine
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