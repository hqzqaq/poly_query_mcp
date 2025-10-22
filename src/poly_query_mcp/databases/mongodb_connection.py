"""
MongoDB数据库连接实现
"""

import logging
from typing import Any, Dict, List, Optional, Union
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId
import json

from .base import DatabaseConnection

logger = logging.getLogger(__name__)


class MongoDBConnection(DatabaseConnection):
    """MongoDB数据库连接"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.current_database = None
    
    def connect(self) -> bool:
        """连接MongoDB数据库"""
        try:
            host = self.config.get("host", "localhost")
            port = self.config.get("port", 27017)
            username = self.config.get("username")
            password = self.config.get("password")
            database = self.config.get("database")
            
            # 构建连接字符串
            if username and password:
                connection_string = f"mongodb://{username}:{password}@{host}:{port}"
            else:
                connection_string = f"mongodb://{host}:{port}"
            
            self.connection = MongoClient(connection_string)
            
            # 测试连接
            self.connection.admin.command('ping')
            
            # 设置默认数据库
            if database:
                self.current_database = self.connection[database]
            
            self.is_connected = True
            logger.info(f"成功连接到MongoDB数据库: {host}:{port}")
            return True
        except Exception as e:
            logger.error(f"连接MongoDB数据库失败: {str(e)}")
            self.is_connected = False
            return False
    
    def disconnect(self) -> bool:
        """断开MongoDB数据库连接"""
        try:
            if self.connection:
                self.connection.close()
                self.is_connected = False
                self.current_database = None
                logger.info("已断开MongoDB数据库连接")
                return True
            return False
        except Exception as e:
            logger.error(f"断开MongoDB数据库连接失败: {str(e)}")
            return False
    
    def execute_query(self, collection: str, operation: str, query: Optional[Dict[str, Any]] = None, 
                     projection: Optional[Dict[str, Any]] = None, 
                     limit: Optional[int] = None, 
                     sort: Optional[List[tuple]] = None) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """执行MongoDB查询"""
        if not self.is_connected:
            if not self.connect():
                raise Exception("无法连接到MongoDB数据库")
        
        try:
            # 只允许执行查询相关的操作
            allowed_operations = {
                'find', 'findOne', 'count', 'distinct', 'aggregate'
            }
            
            if operation not in allowed_operations:
                raise Exception(f"不允许执行操作: {operation}，仅允许执行查询相关操作")
            
            # 确保选择了数据库
            if not self.current_database:
                raise Exception("未选择数据库，请在配置中指定database参数")
            
            db_collection = self.current_database[collection]
            result = None
            
            # 根据操作类型执行查询
            if operation == 'find':
                cursor = db_collection.find(query or {}, projection or {})
                if sort:
                    cursor = cursor.sort(sort)
                if limit:
                    cursor = cursor.limit(limit)
                result = list(cursor)
            
            elif operation == 'findOne':
                result = db_collection.find_one(query or {}, projection or {})
            
            elif operation == 'count':
                result = db_collection.count_documents(query or {})
            
            elif operation == 'distinct':
                if not query or 'field' not in query:
                    raise Exception("distinct操作需要指定field参数")
                field = query['field']
                filter_query = query.get('filter', {})
                result = db_collection.distinct(field, filter_query)
            
            elif operation == 'aggregate':
                if not query or 'pipeline' not in query:
                    raise Exception("aggregate操作需要指定pipeline参数")
                pipeline = query['pipeline']
                cursor = db_collection.aggregate(pipeline)
                result = list(cursor)
            
            # 格式化结果
            formatted_result = self._format_result(result)
            
            return {
                "success": True,
                "data": formatted_result,
                "operation": operation,
                "collection": collection,
                "query": query
            }
        
        except Exception as e:
            logger.error(f"执行MongoDB查询失败: {str(e)}")
            raise
    
    def _format_result(self, result: Any) -> Any:
        """格式化MongoDB结果"""
        if isinstance(result, list):
            return [self._format_result(item) for item in result]
        elif isinstance(result, dict):
            # 处理ObjectId
            formatted = {}
            for key, value in result.items():
                if isinstance(value, ObjectId):
                    formatted[key] = str(value)
                elif isinstance(value, dict):
                    formatted[key] = self._format_result(value)
                elif isinstance(value, list):
                    formatted[key] = [self._format_result(item) for item in value]
                else:
                    formatted[key] = value
            return formatted
        elif isinstance(result, ObjectId):
            return str(result)
        else:
            return result
    
    def test_connection(self) -> bool:
        """测试MongoDB连接"""
        try:
            if not self.is_connected:
                if not self.connect():
                    return False
            
            self.connection.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"测试MongoDB连接失败: {str(e)}")
            return False
    
    def set_database(self, database_name: str) -> bool:
        """设置当前数据库"""
        try:
            if not self.is_connected:
                if not self.connect():
                    return False
            
            self.current_database = self.connection[database_name]
            logger.info(f"已切换到数据库: {database_name}")
            return True
        except Exception as e:
            logger.error(f"切换数据库失败: {str(e)}")
            return False
    
    def list_databases(self) -> List[str]:
        """列出所有数据库"""
        try:
            if not self.is_connected:
                if not self.connect():
                    return []
            
            databases = self.connection.list_database_names()
            return databases
        except Exception as e:
            logger.error(f"列出数据库失败: {str(e)}")
            return []
    
    def list_collections(self) -> List[str]:
        """列出当前数据库的所有集合"""
        try:
            if not self.is_connected:
                if not self.connect():
                    return []
            
            if not self.current_database:
                raise Exception("未选择数据库")
            
            collections = self.current_database.list_collection_names()
            return collections
        except Exception as e:
            logger.error(f"列出集合失败: {str(e)}")
            return []