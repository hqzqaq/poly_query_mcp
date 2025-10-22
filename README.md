# Poly Query MCP

Poly Query MCP 是一个支持多种数据库查询的MCP(Model Context Protocol)工具，允许您通过MCP协议查询MySQL、PostgreSQL、Redis和MongoDB数据库。

## 功能特性

- 🔌 **多数据库支持**: 支持MySQL、PostgreSQL、Redis和MongoDB
- ⚙️ **灵活配置**: 支持配置文件和环境变量配置
- 🛡️ **错误处理**: 完善的错误处理和异常管理
- 📝 **日志记录**: 结构化的日志记录系统
- 🔧 **MCP协议**: 完全兼容MCP协议，可与Claude等AI助手集成

## 快速开始

### 安装

1. 克隆仓库
```bash
git clone <repository-url>
cd poly_query_mcp
```

2. 创建虚拟环境
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

### 配置

1. 复制示例配置文件
```bash
cp config.example.json config.json
```

2. 编辑配置文件，添加您的数据库连接信息

### 使用

启动MCP服务器：
```bash
python main.py
```

在Claude Desktop中使用：
1. 在Claude Desktop的配置文件中添加此MCP服务器
2. 重启Claude Desktop
3. 在对话中使用数据库查询功能

## 支持的数据库

- MySQL
- PostgreSQL
- Redis
- MongoDB

## 文档

- [安装指南](docs/INSTALLATION.md)
- [API文档](docs/API.md)
- [开发指南](docs/DEVELOPMENT.md)

## 贡献

欢迎贡献！请查看 [贡献指南](CONTRIBUTING.md) 了解如何参与项目。

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。