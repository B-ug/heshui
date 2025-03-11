"""配置管理模块。

处理应用程序配置的保存和加载。
"""
import json
import os
from pathlib import Path
from typing import Any, Dict

from appdirs import user_config_dir

class Config:
    """配置管理类。
    
    负责管理应用程序配置的单例类。
    """
    
    _instance = None
    _default_config = {
        "reminder_interval": 30,  # 提醒间隔（分钟）
        "daily_goal": 2000,  # 每日目标饮水量（ml）
        "reminder_text": "该喝水啦！补充水分很重要哦~",  # 提醒文本
        "mute": False,  # 是否静音
        "start_minimized": False,  # 是否以最小化方式启动
    }
    
    def __new__(cls) -> 'Config':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """初始化配置管理器。"""
        self.config_dir = Path(user_config_dir("heshui"))
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.load_config()
    
    def load_config(self) -> None:
        """从文件加载配置。"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = {**self._default_config, **json.load(f)}
            else:
                self._config = self._default_config.copy()
        except Exception:
            self._config = self._default_config.copy()
    
    def save_config(self) -> None:
        """保存配置到文件。"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项值。
        
        Args:
            key: 配置项键名
            default: 默认值
            
        Returns:
            配置项的值
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置项值。
        
        Args:
            key: 配置项键名
            value: 配置项的新值
        """
        self._config[key] = value
        self.save_config()
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置项。
        
        Returns:
            包含所有配置项的字典
        """
        return self._config.copy() 