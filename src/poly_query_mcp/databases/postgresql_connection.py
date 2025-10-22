"""
PostgreSQL数据库连接实现
"""

import logging
from typing import Any, Dict, List, Optional, Union
import psycopg2
import psycopg2.extras

from .base import DatabaseConnection

logger = logging.getLogger(__name__)


class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL数据库连接"""
    
    def connect(self) -> bool:
        """连接PostgreSQL数据库"""
        try:
            self.connection = psycopg2.connect(
                host=self.config.get("host"),
                port=self.config.get("port", 5432),
                user=self.config.get("username"),
                password=self.config.get("password"),
                database=self.config.get("database"),
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            self.connection.autocommit = True
            self.is_connected = True
            logger.info(f"成功连接到PostgreSQL数据库: {self.config.get('host')}:{self.config.get('port')}")
            return True
        except Exception as e:
            logger.error(f"连接PostgreSQL数据库失败: {str(e)}")
            self.is_connected = False
            return False
    
    def disconnect(self) -> bool:
        """断开PostgreSQL数据库连接"""
        try:
            if self.connection:
                self.connection.close()
                self.is_connected = False
                logger.info("已断开PostgreSQL数据库连接")
                return True
            return False
        except Exception as e:
            logger.error(f"断开PostgreSQL数据库连接失败: {str(e)}")
            return False
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """执行PostgreSQL查询"""
        if not self.is_connected:
            if not self.connect():
                raise Exception("无法连接到PostgreSQL数据库")
        
        try:
            with self.connection.cursor() as cursor:
                # 检查是否是SELECT查询
                query_upper = query.strip().upper()
                if query_upper.startswith("SELECT") or query_upper.startswith("SHOW") or query_upper.startswith("DESCRIBE") or query_upper.startswith("EXPLAIN") or query_upper.startswith("\\d"):
                    # 执行查询并返回结果
                    cursor.execute(query, params or {})
                    result = cursor.fetchall()
                    
                    # 转换结果为字典列表
                    formatted_result = []
                    for row in result:
                        formatted_row = dict(row)
                        formatted_result.append(formatted_row)
                    
                    return {
                        "success": True,
                        "data": formatted_result,
                        "row_count": len(formatted_result)
                    }
                else:
                    # 非SELECT查询，不允许执行
                    raise Exception("仅允许执行SELECT、SHOW、DESCRIBE、EXPLAIN和\\d查询")
        
        except Exception as e:
            logger.error(f"执行PostgreSQL查询失败: {str(e)}")
            raise
    
    def test_connection(self) -> bool:
        """测试PostgreSQL连接"""
        try:
            if not self.is_connected:
                if not self.connect():
                    return False
            
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            logger.error(f"测试PostgreSQL连接失败: {str(e)}")
            return False