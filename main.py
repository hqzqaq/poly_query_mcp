"""
Poly Query MCP - 多数据库查询MCP工具入口点
"""

import asyncio
import argparse
import sys
from src.poly_query_mcp.server import main

def print_help():
    """打印帮助信息"""
    help_text = """
Poly Query MCP - 多数据库查询MCP工具

使用方法:
  python main.py [选项]

选项:
  -h, --help     显示此帮助信息
  --version      显示版本信息

描述:
  Poly Query MCP 是一个支持多种数据库查询的MCP(Model Context Protocol)工具。
  支持的数据库类型包括:
  - MySQL
  - PostgreSQL
  - Redis
  - MongoDB

配置:
  请参考 config.example.json 文件创建配置文件，并放置在项目根目录下。
  也可以通过环境变量进行配置。

示例:
  启动MCP服务器:
    python main.py

  在Claude Desktop中使用:
    1. 在Claude Desktop的配置文件中添加此MCP服务器
    2. 重启Claude Desktop
    3. 在对话中使用数据库查询功能
"""
    print(help_text)

def print_version():
    """打印版本信息"""
    print("Poly Query MCP v1.0.0")

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', action='store_true', help='显示帮助信息')
    parser.add_argument('--version', action='store_true', help='显示版本信息')
    
    # 如果没有参数，直接运行MCP服务器
    if len(sys.argv) == 1:
        asyncio.run(main())
        sys.exit(0)
    
    args, unknown = parser.parse_known_args()
    
    if args.help:
        print_help()
    elif args.version:
        print_version()
    else:
        # 运行MCP服务器
        asyncio.run(main())
