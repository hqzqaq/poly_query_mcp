"""
Poly Query MCP - 多数据库查询MCP工具入口点
"""

import asyncio
import argparse
import sys
import json
from src.poly_query_mcp.server import main
from src.poly_query_mcp.utils.enhanced_config_manager import parse_config_args, EnhancedConfigManager
from src.poly_query_mcp.utils.config import AppConfig

def print_help():
    """打印帮助信息"""
    help_text = """
Poly Query MCP - 多数据库查询MCP工具

使用方法:
  python main.py [选项]

选项:
  -h, --help                     显示此帮助信息
  --version                      显示版本信息
  --config FILE                  指定配置文件路径
  --profile NAME                 使用指定的配置文件
  --environment NAME             使用指定的环境配置
  --databases DB1,DB2,...        启用的数据库列表，用逗号分隔

数据库配置覆盖参数:
  --mysql-host HOST              MySQL主机地址
  --mysql-port PORT              MySQL端口
  --mysql-user USER              MySQL用户名
  --mysql-password PASS          MySQL密码
  --mysql-database DB            MySQL数据库名

  --postgresql-host HOST         PostgreSQL主机地址
  --postgresql-port PORT         PostgreSQL端口
  --postgresql-user USER         PostgreSQL用户名
  --postgresql-password PASS     PostgreSQL密码
  --postgresql-database DB       PostgreSQL数据库名
  --postgresql-schema SCHEMA     PostgreSQL模式名(默认为public)

  --redis-host HOST              Redis主机地址
  --redis-port PORT              Redis端口
  --redis-password PASS          Redis密码
  --redis-db DB                  Redis数据库索引

  --mongodb-host HOST            MongoDB主机地址
  --mongodb-port PORT            MongoDB端口
  --mongodb-username USER        MongoDB用户名
  --mongodb-password PASS        MongoDB密码
  --mongodb-database DB          MongoDB数据库名

描述:
  Poly Query MCP 是一个支持多种数据库查询的MCP(Model Context Protocol)工具。
  支持的数据库类型包括:
  - MySQL
  - PostgreSQL
  - Redis
  - MongoDB

配置:
  支持多种配置方式:
  1. 使用配置文件 (config.json 或 config.enhanced.json)
  2. 使用命令行参数
  3. 使用环境变量
  4. 组合使用以上方式

  增强版配置文件(config.enhanced.json)支持多环境和配置文件功能，便于管理不同环境的数据库配置。
  
  配置方法说明:
  1. 使用配置文件:
     python main.py --config /path/to/config.json
  2. 使用增强型配置文件:
     python main.py --config-enhanced /path/to/config.enhanced.json --environment development
  3. 命令行参数:
     python main.py --mysql-host localhost --mysql-port 3306 --mysql-user root --mysql-password password --mysql-database mydb
  4. 混合使用（优先级从高到低）:
     python main.py --config /path/to/config.json --config-enhanced /path/to/config.enhanced.json --environment development --mysql-host localhost

示例:
  启动MCP服务器:
    python main.py

  使用指定配置文件:
    python main.py --profile local

  使用指定环境:
    python main.py --environment production

  仅启用MySQL和PostgreSQL:
    python main.py --databases mysql,postgresql

  覆盖MySQL配置:
    python main.py --mysql-host 192.168.1.100 --mysql-user myuser --mysql-password mypass

  在Claude Desktop中使用:
    1. 在Claude Desktop的配置文件中添加此MCP服务器
    2. 重启Claude Desktop
    3. 在对话中使用数据库查询功能

MCP配置示例:
  # 使用普通配置文件
  {
    "mcpServers": {
      "poly-query-mcp": {
        "command": "python",
        "args": ["/path/to/poly_query_mcp/main.py", "--config", "/path/to/config.json"]
      }
    }
  }

  # 使用增强型配置文件
  {
    "mcpServers": {
      "poly-query-mcp": {
        "command": "python",
        "args": ["/path/to/poly_query_mcp/main.py", "--config-enhanced", "/path/to/config.enhanced.json", "--environment", "development"]
      }
    }
  }

  # 使用命令行参数
  {
    "mcpServers": {
      "poly-query-mcp": {
        "command": "python",
        "args": ["/path/to/poly_query_mcp/main.py", "--mysql-host", "localhost", "--mysql-port", "3306", "--mysql-user", "root", "--mysql-password", "password", "--mysql-database", "mydb"]
      }
    }
  }
"""
    print(help_text)

def print_version():
    """打印版本信息"""
    print("Poly Query MCP v1.0.0")

def print_config_info(passed_args=None):
    """打印当前配置信息"""
    try:
        # 解析配置参数，使用传入的参数或当前命令行参数
        config_args = parse_config_args(passed_args)
        
        # 打印调试信息
        print(f"调试信息 - 命令行参数解析结果:")
        print(f"  配置文件: {config_args.get('config_file')}")
        print(f"  增强型配置文件: {config_args.get('config_enhanced')}")
        print(f"  配置文件名称: {config_args.get('profile')}")
        print(f"  环境: {config_args.get('environment')}")
        print(f"  数据库列表: {config_args.get('databases')}")
        print(f"  配置覆盖: {config_args.get('config_overrides')}")
        
        # 创建配置管理器
        config_file_path = config_args.get("config_file")
        config_manager = EnhancedConfigManager()
        
        # 重新加载配置以应用命令行参数
        config_manager.load_config(
            config_file=config_file_path,
            profile=config_args.get("profile"),
            environment=config_args.get("environment"),
            databases=config_args.get("databases"),
            config_overrides=config_args.get("config_overrides")
        )
        
        # 获取配置
        config = config_manager.get_config()
        
        # 如果指定了增强型配置文件，则加载并合并配置
        if config_args.get("config_enhanced"):
            from src.poly_query_mcp.utils.database_config_manager import DatabaseConfigManager
            db_config_manager = DatabaseConfigManager()
            
            # 使用传入的参数或当前命令行参数
            command_line_args = passed_args if passed_args is not None else sys.argv[1:]
            
            # 加载并合并配置
            final_config = db_config_manager.load_and_merge_config(
                command_line_args=command_line_args,
                normal_config_file=config_args.get("config_file"),
                enhanced_config_file=config_args.get("config_enhanced"),
                environment=config_args.get("environment")
            )
            
            # 更新配置
            config_dict = config.model_dump()
            merged_config_dict = {**config_dict, **final_config}
            config_manager.config = AppConfig.load_from_dict(merged_config_dict)
        
        print("\n当前配置信息:")
        # 判断是否使用了增强型配置文件
        is_enhanced = config_args.get("config_enhanced") is not None
        print(f"  配置类型: {'增强版' if is_enhanced else '传统版'}")
        
        if is_enhanced:
            print(f"  当前环境: {config_args.get('environment', 'default')}")
            if config_args.get("profile"):
                print(f"  当前配置文件: {config_args.get('profile')}")
            
            # 如果需要显示可用环境和配置文件，可以在这里添加
        
        print("\n数据库配置:")
        # 使用合并后的最终配置
        final_config = config_manager.config
        if hasattr(final_config, 'mysql') and final_config.mysql:
            print(f"  MySQL: {final_config.mysql.host}:{final_config.mysql.port}/{final_config.mysql.database}")
        if hasattr(final_config, 'postgresql') and final_config.postgresql:
            print(f"  PostgreSQL: {final_config.postgresql.host}:{final_config.postgresql.port}/{final_config.postgresql.database}")
        if hasattr(final_config, 'redis') and final_config.redis:
            print(f"  Redis: {final_config.redis.host}:{final_config.redis.port}/{final_config.redis.db}")
        if hasattr(final_config, 'mongodb') and final_config.mongodb:
            print(f"  MongoDB: {final_config.mongodb.host}:{final_config.mongodb.port}/{final_config.mongodb.database}")
        
    except Exception as e:
        print(f"获取配置信息失败: {str(e)}")

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', action='store_true', help='显示帮助信息')
    parser.add_argument('--version', action='store_true', help='显示版本信息')
    parser.add_argument('--config-info', action='store_true', help='显示当前配置信息')
    parser.add_argument('--config', type=str, help='指定配置文件路径')
    parser.add_argument('--config-enhanced', type=str, help='指定增强型配置文件路径')
    
    # 如果没有参数，直接运行MCP服务器
    if len(sys.argv) == 1:
        asyncio.run(main())
        sys.exit(0)
    
    args, unknown = parser.parse_known_args()
    
    # 处理特殊选项
    if args.help:
        print_help()
        sys.exit(0)
    elif args.version:
        print_version()
        sys.exit(0)
    elif args.config_info:
        # 构建传递给print_config_info的参数列表
        config_info_args = []
        
        # 添加--config参数
        if args.config:
            config_info_args.extend(['--config', args.config])
        
        # 添加--config-enhanced参数
        if args.config_enhanced:
            config_info_args.extend(['--config-enhanced', args.config_enhanced])
        
        # 添加其他未知参数（可能包含数据库覆盖参数）
        config_info_args.extend(unknown)
        
        print_config_info(config_info_args)
        sys.exit(0)
    else:
        # 直接运行MCP服务器，保留所有参数
        asyncio.run(main())
