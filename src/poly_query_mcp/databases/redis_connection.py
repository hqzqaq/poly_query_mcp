"""
Redis数据库连接实现
"""

import logging
from typing import Any, Dict, List, Optional, Union
import redis
import json
from redis.exceptions import RedisError

from .base import DatabaseConnection

logger = logging.getLogger(__name__)


class RedisConnection(DatabaseConnection):
    """Redis数据库连接"""
    
    def connect(self) -> bool:
        """连接Redis数据库"""
        try:
            self.connection = redis.Redis(
                host=self.config.get("host"),
                port=self.config.get("port", 6379),
                db=self.config.get("db", 0),
                password=self.config.get("password"),
                decode_responses=True
            )
            # 测试连接
            self.connection.ping()
            self.is_connected = True
            logger.info(f"成功连接到Redis数据库: {self.config.get('host')}:{self.config.get('port')}")
            return True
        except Exception as e:
            logger.error(f"连接Redis数据库失败: {str(e)}")
            self.is_connected = False
            return False
    
    def disconnect(self) -> bool:
        """断开Redis数据库连接"""
        try:
            if self.connection:
                self.connection.close()
                self.is_connected = False
                logger.info("已断开Redis数据库连接")
                return True
            return False
        except Exception as e:
            logger.error(f"断开Redis数据库连接失败: {str(e)}")
            return False
    
    def execute_query(self, command: str, args: Optional[List[Any]] = None) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """执行Redis命令"""
        if not self.is_connected:
            if not self.connect():
                raise Exception("无法连接到Redis数据库")
        
        try:
            # 只允许执行查询相关的命令
            allowed_commands = {
                'GET', 'MGET', 'HGET', 'HMGET', 'HGETALL', 'KEYS', 'SCAN', 
                'SSCAN', 'HSCAN', 'ZSCAN', 'SMEMBERS', 'ZRANGE', 'ZREVRANGE',
                'ZRANGEBYSCORE', 'ZCARD', 'SCARD', 'HLEN', 'HKEYS', 'HVALS',
                'EXISTS', 'HEXISTS', 'TYPE', 'TTL', 'PTTL', 'STRLEN', 'LLEN',
                'LRANGE', 'LINDEX', 'INFO', 'CONFIG', 'PING', 'ECHO'
            }
            
            command_upper = command.upper()
            if command_upper not in allowed_commands:
                raise Exception(f"不允许执行命令: {command}，仅允许执行查询相关命令")
            
            # 执行命令
            command_lower = command.lower()
            if not args:
                result = getattr(self.connection, command_lower)()
            else:
                # 处理SCAN命令的特殊情况
                if command_upper in ['SCAN', 'SSCAN', 'HSCAN', 'ZSCAN']:
                    if len(args) < 1:
                        raise Exception(f"{command} 命令需要至少一个参数")
                    
                    cursor = args[0]
                    match_pattern = None
                    count = None
                    
                    # 解析可选参数
                    for i in range(1, len(args)):
                        if isinstance(args[i], str) and args[i].upper() == 'MATCH':
                            if i + 1 < len(args):
                                match_pattern = args[i + 1]
                        elif isinstance(args[i], str) and args[i].upper() == 'COUNT':
                            if i + 1 < len(args):
                                count = int(args[i + 1])
                    
                    if command_upper == 'SCAN':
                        result = self.connection.scan(cursor, match=match_pattern, count=count)
                    elif command_upper == 'SSCAN':
                        result = self.connection.sscan(args[1], cursor, match=match_pattern, count=count)
                    elif command_upper == 'HSCAN':
                        result = self.connection.hscan(args[1], cursor, match=match_pattern, count=count)
                    elif command_upper == 'ZSCAN':
                        result = self.connection.zscan(args[1], cursor, match=match_pattern, count=count)
                else:
                    # 其他命令
                    result = getattr(self.connection, command_lower)(*args)
            
            # 格式化结果
            formatted_result = self._format_result(result)
            
            return {
                "success": True,
                "data": formatted_result,
                "command": f"{command} {' '.join(map(str, args)) if args else ''}"
            }
        
        except Exception as e:
            logger.error(f"执行Redis命令失败: {str(e)}")
            raise
    
    def _format_result(self, result: Any) -> Any:
        """格式化Redis结果"""
        if isinstance(result, bytes):
            try:
                return result.decode('utf-8')
            except UnicodeDecodeError:
                return str(result)
        elif isinstance(result, list):
            return [self._format_result(item) for item in result]
        elif isinstance(result, dict):
            return {k: self._format_result(v) for k, v in result.items()}
        elif isinstance(result, set):
            return [self._format_result(item) for item in result]
        elif isinstance(result, tuple):
            # 处理SCAN命令返回的(cursor, items)元组
            if len(result) == 2:
                cursor, items = result
                return {
                    "cursor": cursor,
                    "items": self._format_result(items)
                }
            else:
                return tuple(self._format_result(item) for item in result)
        else:
            return result
    
    def test_connection(self) -> bool:
        """测试Redis连接"""
        try:
            if not self.is_connected:
                if not self.connect():
                    return False
            
            self.connection.ping()
            return True
        except Exception as e:
            logger.error(f"测试Redis连接失败: {str(e)}")
            return False