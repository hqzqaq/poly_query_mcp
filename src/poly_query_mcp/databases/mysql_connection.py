"""
MySQL数据库连接实现
"""

import logging
from typing import Any, Dict, List, Optional, Union
import pymysql
from pymysql.cursors import DictCursor

from .base import DatabaseConnection

logger = logging.getLogger(__name__)


class MySQLConnection(DatabaseConnection):
    """MySQL数据库连接"""
    
    def connect(self) -> bool:
        """连接MySQL数据库"""
        try:
            self.connection = pymysql.connect(
                host=self.config.get("host"),
                port=self.config.get("port", 3306),
                user=self.config.get("user") or self.config.get("username"),  # 支持两种字段名
                password=self.config.get("password"),
                database=self.config.get("database"),
                charset=self.config.get("charset", "utf8mb4"),
                cursorclass=DictCursor,
                autocommit=True
            )
            self.is_connected = True
            logger.info(f"成功连接到MySQL数据库: {self.config.get('host')}:{self.config.get('port')}")
            return True
        except Exception as e:
            logger.error(f"连接MySQL数据库失败: {str(e)}")
            self.is_connected = False
            return False
    
    def disconnect(self) -> bool:
        """断开MySQL数据库连接"""
        try:
            if self.connection:
                self.connection.close()
                self.is_connected = False
                logger.info("已断开MySQL数据库连接")
                return True
            return False
        except Exception as e:
            logger.error(f"断开MySQL数据库连接失败: {str(e)}")
            return False
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """执行MySQL查询"""
        if not self.is_connected:
            if not self.connect():
                raise Exception("无法连接到MySQL数据库")
        
        try:
            with self.connection.cursor() as cursor:
                # 检查是否是SELECT查询
                query_upper = query.strip().upper()
                if query_upper.startswith("SELECT") or query_upper.startswith("SHOW") or query_upper.startswith("DESCRIBE") or query_upper.startswith("EXPLAIN"):
                    # 执行查询并返回结果
                    cursor.execute(query, params or ())
                    result = cursor.fetchall()
                    
                    # 获取列信息
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    
                    # 格式化结果
                    formatted_result = []
                    for row in result:
                        formatted_row = {}
                        for i, column in enumerate(columns):
                            formatted_row[column] = row.get(column)
                        formatted_result.append(formatted_row)
                    
                    return {
                        "success": True,
                        "data": formatted_result,
                        "row_count": len(formatted_result)
                    }
                else:
                    # 非SELECT查询，不允许执行
                    raise Exception("仅允许执行SELECT、SHOW、DESCRIBE和EXPLAIN查询")
        
        except Exception as e:
            logger.error(f"执行MySQL查询失败: {str(e)}")
            raise
    
    def test_connection(self) -> bool:
        """测试MySQL连接"""
        try:
            if not self.is_connected:
                if not self.connect():
                    return False
            
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            logger.error(f"测试MySQL连接失败: {str(e)}")
            return False