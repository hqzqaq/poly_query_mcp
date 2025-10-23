"""
Poly Query MCP - 多数据库查询MCP工具入口点
"""

import asyncio
import argparse
import sys
import json
from src.poly_query_mcp.server import main
from src.poly_query_mcp.utils.enhanced_config_manager import parse_config_args, EnhancedConfigManager

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
  {
    "mcpServers": {
      "poly-query-mcp": {
        "command": "/Users/hqzqaq/project/python/poly_query_mcp/.venv/bin/python",
        "args": [
          "/Users/hqzqaq/project/python/poly_query_mcp/main.py",
          "--profile", "production"
        ]
      }
    }
  }

  或者直接指定数据库配置:
  {
    "mcpServers": {
      "poly-query-mcp": {
        "command": "/Users/hqzqaq/project/python/poly_query_mcp/.venv/bin/python",
        "args": [
          "/Users/hqzqaq/project/python/poly_query_mcp/main.py",
          "--mysql-host", "localhost",
          "--mysql-port", "3306",
          "--mysql-user", "mysql_user",
          "--mysql-password", "mysql_password",
          "--mysql-database", "mysql_database",
          "--postgresql-host", "localhost",
          "--postgresql-port", "5432",
          "--postgresql-user", "postgre_user",
          "--postgresql-password", "postgre_password",
          "--postgresql-database", "postgre_database"
        ]
      }
    }
  }
"""
    print(help_text)

def print_version():
    """打印版本信息"""
    print("Poly Query MCP v1.0.0")

def print_config_info():
    """打印当前配置信息"""
    try:
        # 解析配置参数
        config_args = parse_config_args()
        
        # 打印调试信息
        print(f"调试信息 - 命令行参数解析结果:")
        print(f"  配置文件: {config_args.get('config_file')}")
        print(f"  配置文件名称: {config_args.get('profile')}")
        print(f"  环境: {config_args.get('environment')}")
        print(f"  数据库列表: {config_args.get('databases')}")
        print(f"  配置覆盖: {config_args.get('config_overrides')}")
        
        # 创建配置管理器
        config_manager = EnhancedConfigManager(config_args.get("config_file"))
        
        # 重新加载配置以应用命令行参数
        config_manager.load_config(
            profile=config_args.get("profile"),
            environment=config_args.get("environment"),
            databases=config_args.get("databases"),
            config_overrides=config_args.get("config_overrides")
        )
        
        # 获取配置
        config = config_manager.get_config()
        
        print("\n当前配置信息:")
        print(f"  配置类型: {'增强版' if config_manager.is_enhanced_config() else '传统版'}")
        
        if config_manager.is_enhanced_config():
            print(f"  当前环境: {config_manager.get_current_environment()}")
            if config_manager.get_current_profile():
                print(f"  当前配置文件: {config_manager.get_current_profile()}")
            
            print("\n可用环境:")
            for env in config_manager.list_environments():
                print(f"  - {env}")
            
            print("\n可用配置文件:")
            for profile in config_manager.list_profiles():
                profile_info = config.config.profiles[profile]
                print(f"  - {profile}: {profile_info.description}")
        
        print("\n数据库配置:")
        if hasattr(config, 'mysql') and config.mysql:
            print(f"  MySQL: {config.mysql.host}:{config.mysql.port}/{config.mysql.database}")
        if hasattr(config, 'postgresql') and config.postgresql:
            print(f"  PostgreSQL: {config.postgresql.host}:{config.postgresql.port}/{config.postgresql.database}")
        if hasattr(config, 'redis') and config.redis:
            print(f"  Redis: {config.redis.host}:{config.redis.port}/{config.redis.db}")
        if hasattr(config, 'mongodb') and config.mongodb:
            print(f"  MongoDB: {config.mongodb.host}:{config.mongodb.port}/{config.mongodb.database}")
        
    except Exception as e:
        print(f"获取配置信息失败: {str(e)}")

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', action='store_true', help='显示帮助信息')
    parser.add_argument('--version', action='store_true', help='显示版本信息')
    parser.add_argument('--config-info', action='store_true', help='显示当前配置信息')
    
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
        # 保存原始参数
        original_argv = sys.argv
        try:
            # 修改参数列表，只保留程序名和未知参数
            sys.argv = [original_argv[0]] + unknown
            print_config_info()
        finally:
            # 恢复原始参数
            sys.argv = original_argv
        sys.exit(0)
    else:
        # 保存原始参数
        original_argv = sys.argv
        try:
            # 修改参数列表，只保留程序名和未知参数
            sys.argv = [original_argv[0]] + unknown
            asyncio.run(main())
        finally:
            # 恢复原始参数
            sys.argv = original_argv
