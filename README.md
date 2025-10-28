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

#### 使用uv安装（推荐）

```bash
# 从PyPI安装
uv add poly-query-mcp

# 或者从GitHub安装
uv add git+https://github.com/yourusername/poly-query-mcp.git

# 或者使用uvx直接运行
uvx poly-query-mcp
```

#### 传统安装方式

1. 克隆仓库
```bash
git clone <repository-url>
cd poly_query_mcp
```

2. 创建虚拟环境
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

### 配置

1. 复制示例配置文件
```bash
cp config.json config.json
```

2. 编辑配置文件，添加您的数据库连接信息

### 使用

启动MCP服务器：
```bash
# 使用uvx
uvx poly-query-mcp

# 或者传统方式
python main.py
```

mcp接入使用：
1. 在支持mcp client中（如Claude Desktop）的配置文件中添加此MCP服务器（参考下面完整的mcp的数据库配置）：

```json
{
  "mcpServers": {
    "poly-query-mcp": {
      "command": "uvx",
      "args": [
        "poly-query-mcp",
        "--mysql-host", "localhost",
        "--mysql-port", "3306",
        "--mysql-user", "root",
        "--mysql-password", "your_mysql_password",
        "--mysql-database", "your_mysql_database"
      ]
    }
  }
}
```

1. 重启mcp服务
2. 在对话中使用数据库查询功能

更多安装和配置选项请参考 [uv安装指南](docs/UV_INSTALLATION.md)

## 数据库配置

Poly Query MCP 支持多种配置方式，包括传统配置文件、增强配置文件和环境变量。您可以根据需要选择最适合的配置方式。

### 1. 直接传入数据库参数
```json
{
  "mcpServers": {
    "poly-query-mcp": {
      "command": "uvx",
      "args": [
        "poly-query-mcp",
        "--mysql-host", "localhost",
        "--mysql-port", "3306",
        "--mysql-user", "root",
        "--mysql-password", "password",
        "--mysql-database", "mysql_database",
        "--postgresql-host", "localhost",
        "--postgresql-port", "5432",
        "--postgresql-user", "postgres",
        "--postgresql-password", "password",
        "--postgresql-database", "postgresql_database",
        "--redis-host", "localhost",
        "--redis-port", "6379",
        "--redis-db", "0",
        "--redis-password", "redis_password",
        "--mongodb-host", "localhost",
        "--mongodb-port", "27017",
        "--mongodb-username", "dev_user",
        "--mongodb-password", "dev_mongodb_password",
        "--mongodb-database", "test"
      ]
    }
  }
}
```


### 2. 传统配置文件

创建一个 `config.json` 文件，包含所有数据库的连接信息：

```json
{
  "mysql": {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "your_mysql_password",
    "database": "your_mysql_database",
    "charset": "utf8mb4"
  },
  "postgresql": {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "your_postgresql_password",
    "database": "your_postgresql_database",
    "pg_schema": "public"
  },
  "redis": {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "password": "your_redis_password"
  },
  "mongodb": {
    "host": "localhost",
    "port": 27017,
    "username": "your_mongodb_username",
    "password": "your_mongodb_password",
    "database": "your_mongodb_database"
  }
}
```

mcp 配置为：
```json
{
  "mcpServers": {
    "poly-query-mcp": {
      "command": "uvx",
      "args": [
        "poly-query-mcp",
        "--config",
        "/path/to/config.json",
      ]
    }
  }
}
```

### 3. 增强配置文件（推荐）

增强配置文件支持多环境配置和配置文件，适合复杂的部署场景。创建 `config.enhanced.json` 文件：

```json
{
  "environments": {
    "development": {
      "mysql": {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "dev_mysql_password",
        "database": "dev_db",
        "charset": "utf8mb4"
      },
      "postgresql": {
        "host": "localhost",
        "port": 5432,
        "user": "postgres",
        "password": "dev_postgresql_password",
        "database": "dev_db",
        "pg_schema": "public"
      },
      "redis": {
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "password": "dev_redis_password"
      },
      "mongodb": {
        "host": "localhost",
        "port": 27017,
        "username": "dev_user",
        "password": "dev_mongodb_password",
        "database": "dev_db"
      }
    },
    "production": {
      "mysql": {
        "host": "prod-mysql.example.com",
        "port": 3306,
        "user": "app_user",
        "password": "${MYSQL_PROD_PASSWORD}",
        "database": "production_db",
        "charset": "utf8mb4"
      },
      "postgresql": {
        "host": "prod-postgresql.example.com",
        "port": 5432,
        "user": "app_user",
        "password": "${POSTGRESQL_PROD_PASSWORD}",
        "database": "production_db",
        "pg_schema": "public"
      },
      "redis": {
        "host": "prod-redis.example.com",
        "port": 6379,
        "db": 0,
        "password": "${REDIS_PROD_PASSWORD}"
      },
      "mongodb": {
        "host": "prod-mongodb.example.com",
        "port": 27017,
        "username": "app_user",
        "password": "${MONGODB_PROD_PASSWORD}",
        "database": "production_db"
      }
    }
  },
  "profiles": {
    "local": {
      "environment": "development",
      "description": "本地开发环境配置"
    },
    "staging": {
      "environment": "production",
      "description": "预发布环境配置"
    },
    "minimal": {
      "environment": "development",
      "databases": ["mysql"],
      "description": "仅MySQL数据库的轻量级配置"
    }
  },
  "defaults": {
    "environment": "development",
    "log_level": "INFO",
    "connection_pool_size": 5,
    "connection_timeout": 30
  }
}
```

mcp的配置为：
```json
{
  "mcpServers": {
    "poly-query-mcp": {
      "command": "uvx",
      "args": [
        "poly-query-mcp",
        "--config-enhanced",
        "/path/to/config.enhanced.json",
        "--environment",
        "development"
      ]
    }
  }
}
```


### 4. 数据库配置详解

#### MySQL 配置

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| host | string | 是 | - | MySQL服务器地址 |
| port | integer | 否 | 3306 | MySQL服务器端口 |
| user | string | 是 | - | MySQL用户名 |
| password | string | 是 | - | MySQL密码 |
| database | string | 是 | - | MySQL数据库名 |
| charset | string | 否 | utf8mb4 | 字符集 |

**使用场景**：
- 适用于需要ACID事务支持的关系型数据存储
- 适用于结构化数据，如用户信息、订单数据等

**注意事项**：
- 确保MySQL用户有足够的权限访问指定的数据库
- 对于生产环境，建议使用SSL连接
- 字符集建议使用utf8mb4以支持完整的Unicode字符集

#### PostgreSQL 配置

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| host | string | 是 | - | PostgreSQL服务器地址 |
| port | integer | 否 | 5432 | PostgreSQL服务器端口 |
| user | string | 是 | - | PostgreSQL用户名 |
| password | string | 是 | - | PostgreSQL密码 |
| database | string | 是 | - | PostgreSQL数据库名 |
| pg_schema | string | 否 | public | PostgreSQL模式名 |

**使用场景**：
- 适用于需要复杂查询和数据分析的场景
- 适用于需要高级数据类型和扩展功能的应用

**注意事项**：
- 确保PostgreSQL用户有足够的权限访问指定的数据库和模式
- 对于生产环境，建议配置连接池以优化性能
- 可以通过pg_schema参数实现多租户隔离

#### Redis 配置

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| host | string | 是 | - | Redis服务器地址 |
| port | integer | 否 | 6379 | Redis服务器端口 |
| password | string | 否 | - | Redis密码（可选） |
| db | integer | 否 | 0 | Redis数据库索引（0-15） |

**使用场景**：
- 适用于缓存、会话存储、消息队列等场景
- 适用于需要高性能读写的数据

**注意事项**：
- Redis数据库索引范围为0-15，确保指定的索引存在
- 对于生产环境，建议配置密码认证
- 考虑使用Redis集群以提高可用性

#### MongoDB 配置

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| host | string | 是 | - | MongoDB服务器地址 |
| port | integer | 否 | 27017 | MongoDB服务器端口 |
| username | string | 否 | - | MongoDB用户名 |
| password | string | 否 | - | MongoDB密码 |
| database | string | 是 | - | MongoDB数据库名 |

**使用场景**：
- 适用于文档型数据存储，如日志、配置等
- 适用于需要灵活数据结构的场景

**注意事项**：
- 确保MongoDB用户有足够的权限访问指定的数据库
- 对于生产环境，建议配置副本集以提高可用性
- 考虑使用索引优化查询性能

### 5. 安全注意事项

1. **密码保护**：
   - 不要在代码中硬编码密码
   - 使用环境变量或配置文件存储敏感信息
   - 对于生产环境，考虑使用密钥管理服务

2. **网络安全**：
   - 在生产环境中使用SSL/TLS连接
   - 限制数据库访问的网络范围
   - 使用防火墙规则限制数据库访问

3. **权限控制**：
   - 为应用程序创建专用的数据库用户
   - 仅授予必要的最小权限
   - 定期轮换数据库密码

### 8. 故障排除

#### 常见问题

1. **连接超时**：
   - 检查数据库服务器是否运行
   - 验证网络连接和防火墙设置
   - 确认主机地址和端口是否正确

2. **认证失败**：
   - 验证用户名和密码是否正确
   - 检查用户是否有访问指定数据库的权限
   - 确认认证插件是否匹配

3. **数据库不存在**：
   - 确认数据库名称是否正确
   - 检查用户是否有创建数据库的权限
   - 验证数据库是否已创建

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