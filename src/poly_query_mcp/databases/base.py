"""
数据库连接基类
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)


class DatabaseConnection(ABC):
    """数据库连接基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
        self.is_connected = False
    
    @abstractmethod
    def connect(self) -> bool:
        """连接数据库"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """断开数据库连接"""
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """执行查询"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """测试连接"""
        pass
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()