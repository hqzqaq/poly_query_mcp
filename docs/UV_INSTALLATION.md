# 使用uv安装和配置Poly Query MCP

## 1. 使用uv安装

### 方法一：直接从GitHub安装（推荐）

```bash
# 安装最新版本
uv add git+https://github.com/yourusername/poly-query-mcp.git

# 或者安装特定版本
uv add git+https://github.com/yourusername/poly-query-mcp.git@v0.1.0
```

### 方法二：从PyPI安装（如果已发布）

```bash
# 安装最新版本
uv add poly-query-mcp

# 或者安装特定版本
uv add poly-query-mcp==0.1.0
```

### 方法三：开发模式安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/poly-query-mcp.git
cd poly-query-mcp

# 使用uv安装开发依赖
uv sync --dev

# 或者以可编辑模式安装
uv pip install -e .
```

## 2. 配置MCP服务器

### 基本配置

在Claude Desktop的配置文件中添加以下内容：

```json
{
  "mcpServers": {
    "poly-query-mcp": {
      "command": "uvx",
      "args": [
        "poly-query-mcp"
      ]
    }
  }
}
```

### 使用配置文件

1. 创建配置文件 `~/.config/poly-query-mcp/config.json`:

```json
{
  "mysql": {
    "host": "your-mysql-host",
    "port": 3306,
    "user": "your-mysql-user",
    "password": "your-mysql-password",
    "database": "your-mysql-database"
  },
  "postgresql": {
    "host": "your-postgresql-host",
    "port": 5432,
    "user": "your-postgresql-user",
    "password": "your-postgresql-password",
    "database": "your-postgresql-database"
  },
  "redis": {
    "host": "your-redis-host",
    "port": 6379,
    "password": "your-redis-password",
    "db": 0
  },
  "mongodb": {
    "host": "your-mongodb-host",
    "port": 27017,
    "username": "your-mongodb-username",
    "password": "your-mongodb-password",
    "database": "your-mongodb-database"
  }
}
```

2. 在Claude Desktop配置中引用配置文件：

```json
{
  "mcpServers": {
    "poly-query-mcp": {
      "command": "uvx",
      "args": [
        "poly-query-mcp",
        "--config", "~/.config/poly-query-mcp/config.json"
      ]
    }
  }
}
```

### 使用环境变量

创建 `.env` 文件：

```env
MYSQL_HOST=your-mysql-host
MYSQL_PORT=3306
MYSQL_USER=your-mysql-user
MYSQL_PASSWORD=your-mysql-password
MYSQL_DATABASE=your-mysql-database

POSTGRESQL_HOST=your-postgresql-host
POSTGRESQL_PORT=5432
POSTGRESQL_USER=your-postgresql-user
POSTGRESQL_PASSWORD=your-postgresql-password
POSTGRESQL_DATABASE=your-postgresql-database

REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_DB=0

MONGODB_HOST=your-mongodb-host
MONGODB_PORT=27017
MONGODB_USERNAME=your-mongodb-username
MONGODB_PASSWORD=your-mongodb-password
MONGODB_DATABASE=your-mongodb-database
```

然后在Claude Desktop配置中：

```json
{
  "mcpServers": {
    "poly-query-mcp": {
      "command": "uvx",
      "args": [
        "poly-query-mcp",
        "--env-file", "/path/to/your/.env"
      ]
    }
  }
}
```

### 直接传递参数

```json
{
  "mcpServers": {
    "poly-query-mcp": {
      "command": "uvx",
      "args": [
        "poly-query-mcp",
        "--mysql-host", "your-mysql-host",
        "--mysql-port", "3306",
        "--mysql-user", "your-mysql-user",
        "--mysql-password", "your-mysql-password",
        "--mysql-database", "your-mysql-database",
        "--postgresql-host", "your-postgresql-host",
        "--postgresql-port", "5432",
        "--postgresql-user", "your-postgresql-user",
        "--postgresql-password", "your-postgresql-password",
        "--postgresql-database", "your-postgresql-database"
      ]
    }
  }
}
```

## 3. 使用uvx运行

uvx是uv提供的工具，可以运行Python应用程序而无需手动安装：

```bash
# 直接运行
uvx poly-query-mcp

# 带参数运行
uvx poly-query-mcp --mysql-host localhost --mysql-user root

# 运行特定版本
uvx poly-query-mcp==0.1.0

# 从GitHub运行
uvx git+https://github.com/yourusername/poly-query-mcp.git
```

## 4. 发布到PyPI

如果你是开发者，想要发布这个包到PyPI：

```bash
# 1. 构建包
uv build

# 2. 发布到测试PyPI
uv publish --publish-url https://test.pypi.org/legacy/

# 3. 发布到正式PyPI
uv publish
```

## 5. 在项目中使用

如果你想在另一个Python项目中使用这个MCP工具：

```bash
# 在你的项目目录中
cd your-project

# 添加为依赖
uv add poly-query-mcp

# 或者从GitHub添加
uv add git+https://github.com/yourusername/poly-query-mcp.git
```

## 6. 更新和维护

```bash
# 更新到最新版本
uv add poly-query-mcp --upgrade

# 更新到特定版本
uv add poly-query-mcp==0.2.0 --upgrade

# 从Git更新
uv add git+https://github.com/yourusername/poly-query-mcp.git --upgrade
```

## 7. 故障排除

### 常见问题

1. **找不到命令**：确保uv已正确安装并在PATH中
2. **权限问题**：可能需要使用`--user`标志或虚拟环境
3. **依赖冲突**：使用`uv tree`查看依赖树
4. **配置问题**：检查配置文件路径和格式

### 调试命令

```bash
# 检查安装
uv pip show poly-query-mcp

# 查看依赖树
uv tree

# 运行测试
uv run pytest

# 检查配置
uvx poly-query-mcp --config-info
```

## 8. 高级用法

### 使用特定Python版本

```bash
# 使用Python 3.12
uv add poly-query-mcp --python 3.12

# 或者创建特定Python版本的环境
uv venv --python 3.12
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate  # Windows
uv add poly-query-mcp
```

### 使用开发版本

```bash
# 安装最新的开发版本
uv add git+https://github.com/yourusername/poly-query-mcp.git@main

# 或者安装特定的分支或提交
uv add git+https://github.com/yourusername/poly-query-mcp.git@feature-branch
uv add git+https://github.com/yourusername/poly-query-mcp.git@commit-hash
```