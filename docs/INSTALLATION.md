# 安装指南

本文档提供了Poly Query MCP工具的详细安装和配置说明。

## 系统要求

- Python 3.8 或更高版本
- 支持的数据库：MySQL 5.7+、PostgreSQL 10+、Redis 5.0+、MongoDB 4.0+

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/poly-query-mcp.git
cd poly-query-mcp
```

### 2. 创建虚拟环境

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Linux/Mac

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置数据库连接

#### 方法一：使用配置文件

1. 复制示例配置文件：
   ```bash
   cp config.example.json config.json
   ```

2. 编辑 `config.json` 文件，添加您的数据库连接信息：

   ```json
   {
     "mysql": {
       "host": "localhost",
       "port": 3306,
       "user": "your_username",
       "password": "your_password",
       "database": "your_database"
     },
     "postgresql": {
       "host": "localhost",
       "port": 5432,
       "user": "your_username",
       "password": "your_password",
       "database": "your_database"
     },
     "redis": {
       "host": "localhost",
       "port": 6379,
       "password": "your_redis_password",
       "database": 0
     },
     "mongodb": {
       "host": "localhost",
       "port": 27017,
       "user": "your_username",
       "password": "your_password",
       "database": "your_database"
     }
   }
   ```

#### 方法二：使用环境变量

您也可以使用环境变量来配置数据库连接：

```bash
# MySQL
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=your_username
export MYSQL_PASSWORD=your_password
export MYSQL_DATABASE=your_database

# PostgreSQL
export POSTGRESQL_HOST=localhost
export POSTGRESQL_PORT=5432
export POSTGRESQL_USER=your_username
export POSTGRESQL_PASSWORD=your_password
export POSTGRESQL_DATABASE=your_database

# Redis
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_PASSWORD=your_redis_password
export REDIS_DATABASE=0

# MongoDB
export MONGODB_HOST=localhost
export MONGODB_PORT=27017
export MONGODB_USER=your_username
export MONGODB_PASSWORD=your_password
export MONGODB_DATABASE=your_database
```

### 5. 配置日志（可选）

您可以通过环境变量配置日志级别和输出文件：

```bash
export POLY_QUERY_LOG_LEVEL=INFO
export POLY_QUERY_LOG_FILE=logs/poly_query.log
```

## 测试安装

1. 启动服务器：
   ```bash
   python main.py
   ```

2. 如果一切正常，您应该看到类似以下的输出：
   ```
   [INFO] Poly Query MCP 服务器启动
   [INFO] 配置加载成功
   [INFO] 服务器运行在 stdio
   ```

## 在MCP客户端中使用

1. 在支持MCP的应用程序中添加此服务器
2. 配置服务器命令：`python /path/to/poly-query_mcp/main.py`
3. 重启应用程序

## 常见问题

### 问题1：模块导入错误

**错误信息**：`ModuleNotFoundError: No module named 'mcp'`

**解决方案**：确保已正确安装所有依赖：
```bash
pip install -r requirements.txt
```

### 问题2：数据库连接失败

**错误信息**：`DatabaseConnectionError: 无法连接到数据库`

**解决方案**：
1. 检查数据库服务是否运行
2. 验证配置文件中的连接参数
3. 确保数据库用户具有足够的权限

### 问题3：权限错误

**错误信息**：`PermissionError: [Errno 13] Permission denied`

**解决方案**：
1. 确保您有读写项目目录的权限
2. 在Linux/Mac上，可能需要使用`sudo`（不推荐）或更改文件权限

### 问题4：虚拟环境激活问题

**Windows**：
```bash
.venv\Scripts\activate
```

**Linux/Mac**：
```bash
source .venv/bin/activate
```

如果激活失败，尝试重新创建虚拟环境：
```bash
python -m venv .venv --clear
```

## 卸载

如需卸载Poly Query MCP：

1. 停止运行中的服务器
2. 删除项目目录：
   ```bash
   cd ..
   rm -rf poly-query-mcp
   ```
3. 从MCP客户端中移除服务器配置

## 获取帮助

如遇到问题，请：
1. 查看本文档的常见问题部分
2. 检查项目的[Issues页面](https://github.com/yourusername/poly-query-mcp/issues)
3. 创建新的Issue并提供详细的错误信息