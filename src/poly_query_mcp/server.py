"""
MCP服务器主文件
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional, Union
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    CallToolRequest,
    ReadResourceRequest,
    ListResourcesRequest,
    ListToolsRequest,
)

from .databases.base import DatabaseConnection
from .databases.mysql_connection import MySQLConnection
from .databases.postgresql_connection import PostgreSQLConnection
from .databases.redis_connection import RedisConnection
from .databases.mongodb_connection import MongoDBConnection
from .utils.config import AppConfig, DatabaseConfig
from .utils.enhanced_config_manager import EnhancedConfigManager, parse_config_args
from .utils.logger import setup_logger
from .utils.exceptions import (
    PolyQueryMCPError,
    DatabaseConnectionError,
    DatabaseQueryError,
    ConfigurationError,
    ValidationError,
    AuthenticationError,
    PermissionError,
    ResourceNotFoundError,
    TimeoutError,
    RateLimitError
)

# 设置日志
log_level = os.getenv("LOG_LEVEL", "INFO")
log_file = os.getenv("LOG_FILE", None)
logger = setup_logger("poly-query-mcp", log_level, log_file)

# 创建MCP服务器实例
server = Server("poly-query-mcp")

# 存储数据库连接
connections: Dict[str, DatabaseConnection] = {}

# 配置管理器
config_manager: Optional[EnhancedConfigManager] = None


def get_connection(db_type: str, config: DatabaseConfig) -> DatabaseConnection:
    """获取数据库连接"""
    try:
        if db_type not in connections:
            if db_type == "mysql":
                connections[db_type] = MySQLConnection(config.dict())
            elif db_type == "postgresql":
                connections[db_type] = PostgreSQLConnection(config.dict())
            elif db_type == "redis":
                connections[db_type] = RedisConnection(config.dict())
            elif db_type == "mongodb":
                connections[db_type] = MongoDBConnection(config.dict())
            else:
                raise ValidationError(f"不支持的数据库类型: {db_type}")
        
        return connections[db_type]
    except Exception as e:
        logger.error(f"获取数据库连接失败: {str(e)}")
        raise DatabaseConnectionError(f"无法获取{db_type}数据库连接: {str(e)}")


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """列出可用工具"""
    return [
        Tool(
            name="query_mysql",
            description="查询MySQL数据库",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL查询语句"
                    },
                    "params": {
                        "type": "object",
                        "description": "查询参数（可选）"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="query_postgresql",
            description="查询PostgreSQL数据库",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL查询语句"
                    },
                    "params": {
                        "type": "object",
                        "description": "查询参数（可选）"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="query_redis",
            description="查询Redis数据库",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Redis命令"
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "命令参数（可选）"
                    }
                },
                "required": ["command"]
            }
        ),
        Tool(
            name="query_mongodb",
            description="查询MongoDB数据库",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection": {
                        "type": "string",
                        "description": "集合名称"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["find", "aggregate", "count"],
                        "description": "操作类型"
                    },
                    "filter": {
                        "type": "object",
                        "description": "查询条件（可选）"
                    },
                    "pipeline": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "聚合管道（可选）"
                    }
                },
                "required": ["collection", "operation"]
            }
        ),
        Tool(
            name="test_connection",
            description="测试数据库连接",
            inputSchema={
                "type": "object",
                "properties": {
                    "db_type": {
                        "type": "string",
                        "enum": ["mysql", "postgresql", "redis", "mongodb"],
                        "description": "数据库类型"
                    }
                },
                "required": ["db_type"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
    """处理工具调用"""
    try:
        logger.info(f"调用工具: {name}, 参数: {json.dumps(arguments, ensure_ascii=False)}")
        
        # 检查配置管理器是否已初始化
        if config_manager is None:
            raise ConfigurationError("配置管理器未初始化")
        
        config = config_manager.get_config()
        
        if name == "query_mysql":
            if not config.mysql:
                raise ConfigurationError("MySQL数据库未配置")
            
            conn = get_connection("mysql", config.mysql)
            if not conn.is_connected:
                conn.connect()
            
            query = arguments.get("query")
            if not query:
                raise ValidationError("缺少必需参数: query")
            
            params = arguments.get("params", {})
            
            result = conn.execute_query(query, params)
            logger.info(f"MySQL查询成功，返回{len(result.get('data', []))}条记录")
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "query_postgresql":
            if not config.postgresql:
                raise ConfigurationError("PostgreSQL数据库未配置")
            
            conn = get_connection("postgresql", config.postgresql)
            if not conn.is_connected:
                conn.connect()
            
            query = arguments.get("query")
            if not query:
                raise ValidationError("缺少必需参数: query")
            
            params = arguments.get("params", {})
            
            result = conn.execute_query(query, params)
            logger.info(f"PostgreSQL查询成功，返回{len(result.get('data', []))}条记录")
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "query_redis":
            if not config.redis:
                raise ConfigurationError("Redis数据库未配置")
            
            conn = get_connection("redis", config.redis)
            if not conn.is_connected:
                conn.connect()
            
            command = arguments.get("command")
            if not command:
                raise ValidationError("缺少必需参数: command")
            
            args = arguments.get("args", [])
            
            result = conn.execute_query(command, args)
            logger.info(f"Redis命令执行成功: {command}")
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "query_mongodb":
            if not config.mongodb:
                raise ConfigurationError("MongoDB数据库未配置")
            
            conn = get_connection("mongodb", config.mongodb)
            if not conn.is_connected:
                conn.connect()
            
            collection = arguments.get("collection")
            if not collection:
                raise ValidationError("缺少必需参数: collection")
            
            operation = arguments.get("operation")
            if not operation:
                raise ValidationError("缺少必需参数: operation")
            
            filter_doc = arguments.get("filter", {})
            pipeline = arguments.get("pipeline", [])
            
            # 根据操作类型构建查询参数
            if operation == "find":
                query_params = {"collection": collection, "filter": filter_doc}
            elif operation == "aggregate":
                query_params = {"collection": collection, "pipeline": pipeline}
            elif operation == "count":
                query_params = {"collection": collection, "filter": filter_doc}
            else:
                raise ValidationError(f"不支持的操作类型: {operation}")
            
            result = conn.execute_query(collection, operation, query_params)
            logger.info(f"MongoDB查询成功，操作: {operation}, 集合: {collection}")
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "test_connection":
            db_type = arguments.get("db_type")
            if not db_type:
                raise ValidationError("缺少必需参数: db_type")
            
            if db_type == "mysql" and config.mysql:
                conn = get_connection("mysql", config.mysql)
                success = conn.test_connection()
                return [TextContent(type="text", text=f"MySQL连接测试: {'成功' if success else '失败'}")]
            
            elif db_type == "postgresql" and config.postgresql:
                conn = get_connection("postgresql", config.postgresql)
                success = conn.test_connection()
                return [TextContent(type="text", text=f"PostgreSQL连接测试: {'成功' if success else '失败'}")]
            
            elif db_type == "redis" and config.redis:
                conn = get_connection("redis", config.redis)
                success = conn.test_connection()
                return [TextContent(type="text", text=f"Redis连接测试: {'成功' if success else '失败'}")]
            
            elif db_type == "mongodb" and config.mongodb:
                conn = get_connection("mongodb", config.mongodb)
                success = conn.test_connection()
                return [TextContent(type="text", text=f"MongoDB连接测试: {'成功' if success else '失败'}")]
            
            else:
                raise ConfigurationError(f"数据库 {db_type} 未配置")
        
        else:
            raise ValidationError(f"未知工具: {name}")
    
    except PolyQueryMCPError as e:
        logger.error(f"工具调用错误: {str(e)}")
        return [TextContent(type="text", text=f"错误: {e.message}")]
    except Exception as e:
        logger.error(f"工具调用未知错误: {str(e)}")
        return [TextContent(type="text", text=f"未知错误: {str(e)}")]


async def main():
    """主函数"""
    # 解析配置参数
    config_args = parse_config_args()
    
    # 打印调试信息
    print(f"调试信息 - server.py main函数:")
    print(f"  配置文件: {config_args.get('config_file')}")
    print(f"  配置文件名称: {config_args.get('profile')}")
    print(f"  环境: {config_args.get('environment')}")
    print(f"  数据库列表: {config_args.get('databases')}")
    print(f"  配置覆盖: {config_args.get('config_overrides')}")
    
    # 创建配置管理器
    global config_manager
    config_manager = EnhancedConfigManager(config_args.get("config_file"))
    
    # 加载配置
    config_manager.load_config(
        profile=config_args.get("profile"),
        environment=config_args.get("environment"),
        databases=config_args.get("databases"),
        config_overrides=config_args.get("config_overrides")
    )
    
    # 打印配置信息
    config = config_manager.get_config()
    print(f"配置加载完成:")
    print(f"  配置类型: {'增强版' if config_manager.is_enhanced_config() else '传统版'}")
    if hasattr(config, 'mysql') and config.mysql:
        print(f"  MySQL: {config.mysql.host}:{config.mysql.port}/{config.mysql.database}")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def cli_main():
    """命令行入口点"""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()