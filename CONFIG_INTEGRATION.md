# Poly Query MCP 配置整合方案

## 概述

本文档详细说明了如何将数据库配置整合到MCP连接命令中，实现人性化、按需配置和多层级结构的配置管理。

## 配置架构

### 1. 配置文件结构

我们支持两种配置文件格式：

#### 传统配置文件 (config.json)
```json
{
  "mysql": {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "password",
    "database": "test"
  },
  "postgresql": {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "password",
    "database": "test"
  },
  "redis": {
    "host": "localhost",
    "port": 6379,
    "password": null,
    "db": 0
  },
  "mongodb": {
    "host": "localhost",
    "port": 27017,
    "username": null,
    "password": null,
    "database": "test"
  }
}
```

#### 增强版配置文件 (config.enhanced.json)
```json
{
  "environments": {
    "development": {
      "mysql": {
        "host": "localhost",
        "port": 3306,
        "user": "dev_user",
        "password": "dev_password",
        "database": "dev_db"
      },
      "postgresql": {
        "host": "localhost",
        "port": 5432,
        "user": "dev_user",
        "password": "dev_password",
        "database": "dev_db"
      },
      "redis": {
        "host": "localhost",
        "port": 6379,
        "password": null,
        "db": 0
      },
      "mongodb": {
        "host": "localhost",
        "port": 27017,
        "username": null,
        "password": null,
        "database": "dev_db"
      }
    },
    "production": {
      "mysql": {
        "host": "localhost",
        "port": 3306,
        "user": "pro",
        "password": "pro_password",
        "database": "pro"
      },
      "postgresql": {
        "host": "localhost",
        "port": 5432,
        "user": "user",
        "password": "password",
        "database": "user"
      },
      "redis": {
        "host": "localhost",
        "port": 6379,
        "password": "redis_password",
        "db": 0
      },
      "mongodb": {
        "host": "localhost",
        "port": 27017,
        "username": "mongo_user",
        "password": "mongo_password",
        "database": "prod_db"
      }
    }
  },
  "profiles": {
    "local": {
      "description": "本地开发环境配置",
      "environment": "development",
      "databases": ["mysql", "postgresql"]
    },
    "remote": {
      "description": "远程生产环境配置",
      "environment": "production",
      "databases": ["mysql", "postgresql", "redis", "mongodb"]
    },
    "mysql_only": {
      "description": "仅使用MySQL数据库",
      "environment": "development",
      "databases": ["mysql"]
    }
  },
  "defaults": {
    "environment": "development",
    "databases": ["mysql", "postgresql", "redis", "mongodb"]
  }
}
```

### 2. 配置层级

配置系统支持以下层级（优先级从高到低）：

1. **命令行参数** - 最高优先级，直接覆盖配置
2. **环境变量** - 次高优先级
3. **配置文件** - 基础配置
4. **默认值** - 最低优先级

## MCP连接配置

### 1. 基本MCP配置

```json
{
  "mcpServers": {
    "poly-query-mcp": {
      "command": "/Users/hqzqaq/project/python/poly_query_mcp/.venv/bin/python",
      "args": [
        "/Users/hqzqaq/project/python/poly_query_mcp/main.py"
      ]
    }
  }
}
```

### 2. 使用配置文件

```json
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
```

### 3. 使用环境配置

```json
{
  "mcpServers": {
    "poly-query-mcp": {
      "command": "/Users/hqzqaq/project/python/poly_query_mcp/.venv/bin/python",
      "args": [
        "/Users/hqzqaq/project/python/poly_query_mcp/main.py",
        "--environment", "production"
      ]
    }
  }
}
```

### 4. 指定特定数据库

```json
{
  "mcpServers": {
    "poly-query-mcp": {
      "command": "/Users/hqzqaq/project/python/poly_query_mcp/.venv/bin/python",
      "args": [
        "/Users/hqzqaq/project/python/poly_query_mcp/main.py",
        "--databases", "mysql,postgresql"
      ]
    }
  }
}
```

### 5. 直接通过命令行参数配置数据库

```json
{
  "mcpServers": {
    "poly-query-mcp": {
      "command": "/Users/hqzqaq/project/python/poly_query_mcp/.venv/bin/python",
      "args": [
        "/Users/hqzqaq/project/python/poly_query_mcp/main.py",
        "--mysql-host", "localhost",
        "--mysql-port", "3306",
        "--mysql-user", "user",
        "--mysql-password", "password",
        "--mysql-database", "moss",
        "--postgresql-host", "localhost",
        "--postgresql-port", "5432",
        "--postgresql-user", "user",
        "--postgresql-password", "password",
        "--postgresql-database", "user"
      ]
    }
  }
}
```

### 6. 组合使用多种配置方式

```json
{
  "mcpServers": {
    "poly-query-mcp": {
      "command": "/Users/hqzqaq/project/python/poly_query_mcp/.venv/bin/python",
      "args": [
        "/Users/hqzqaq/project/python/poly_query_mcp/main.py",
        "--profile", "production",
        "--mysql-host", "backup.mysql.server",
        "--redis-host", "backup.redis.server"
      ]
    }
  }
}
```

## 使用场景

### 1. 开发环境

在开发环境中，可以使用本地数据库配置：

```json
{
  "mcpServers": {
    "poly-query-mcp": {
      "command": "/Users/hqzqaq/project/python/poly_query_mcp/.venv/bin/python",
      "args": [
        "/Users/hqzqaq/project/python/poly_query_mcp/main.py",
        "--profile", "local"
      ]
    }
  }
}
```

### 2. 生产环境

在生产环境中，使用生产数据库配置：

```json
{
  "mcpServers": {
    "poly-query-mcp": {
      "command": "/Users/hqzqaq/project/python/poly_query_mcp/.venv/bin/python",
      "args": [
        "/Users/hqzqaq/project/python/poly_query_mcp/main.py",
        "--profile", "remote"
      ]
    }
  }
}
```

### 3. 特定任务

对于只需要特定数据库的任务，可以指定数据库列表：

```json
{
  "mcpServers": {
    "poly-query-mcp": {
      "command": "/Users/hqzqaq/project/python/poly_query_mcp/.venv/bin/python",
      "args": [
        "/Users/hqzqaq/project/python/poly_query_mcp/main.py",
        "--profile", "production",
        "--databases", "mysql"
      ]
    }
  }
}
```

### 4. 临时连接

对于临时连接到特定数据库，可以直接指定连接参数：

```json
{
  "mcpServers": {
    "poly-query-mcp": {
      "command": "/Users/hqzqaq/project/python/poly_query_mcp/.venv/bin/python",
      "args": [
        "/Users/hqzqaq/project/python/poly_query_mcp/main.py",
        "--mysql-host", "temp.server.com",
        "--mysql-port", "3306",
        "--mysql-user", "temp_user",
        "--mysql-password", "temp_password",
        "--mysql-database", "temp_db",
        "--databases", "mysql"
      ]
    }
  }
}
```

## 命令行参数参考

### 基本参数

- `--config FILE`: 指定配置文件路径
- `--profile NAME`: 使用指定的配置文件
- `--environment NAME`: 使用指定的环境配置
- `--databases DB1,DB2,...`: 启用的数据库列表，用逗号分隔
- `--help`: 显示帮助信息
- `--version`: 显示版本信息
- `--config-info`: 显示当前配置信息

### 数据库特定参数

#### MySQL
- `--mysql-host HOST`: MySQL主机地址
- `--mysql-port PORT`: MySQL端口
- `--mysql-user USER`: MySQL用户名
- `--mysql-password PASS`: MySQL密码
- `--mysql-database DB`: MySQL数据库名

#### PostgreSQL
- `--postgresql-host HOST`: PostgreSQL主机地址
- `--postgresql-port PORT`: PostgreSQL端口
- `--postgresql-user USER`: PostgreSQL用户名
- `--postgresql-password PASS`: PostgreSQL密码
- `--postgresql-database DB`: PostgreSQL数据库名

#### Redis
- `--redis-host HOST`: Redis主机地址
- `--redis-port PORT`: Redis端口
- `--redis-password PASS`: Redis密码
- `--redis-db DB`: Redis数据库索引

#### MongoDB
- `--mongodb-host HOST`: MongoDB主机地址
- `--mongodb-port PORT`: MongoDB端口
- `--mongodb-username USER`: MongoDB用户名
- `--mongodb-password PASS`: MongoDB密码
- `--mongodb-database DB`: MongoDB数据库名

## 环境变量

除了命令行参数，还可以使用环境变量进行配置：

```bash
# 基本配置
export POLY_QUERY_CONFIG_FILE="/path/to/config.json"
export POLY_QUERY_PROFILE="production"
export POLY_QUERY_ENVIRONMENT="production"
export POLY_QUERY_DATABASES="mysql,postgresql"

# MySQL配置
export POLY_QUERY_MYSQL_HOST="localhost"
export POLY_QUERY_MYSQL_PORT="3306"
export POLY_QUERY_MYSQL_USER="user"
export POLY_QUERY_MYSQL_PASSWORD="password"
export POLY_QUERY_MYSQL_DATABASE="database"

# PostgreSQL配置
export POLY_QUERY_POSTGRESQL_HOST="localhost"
export POLY_QUERY_POSTGRESQL_PORT="5432"
export POLY_QUERY_POSTGRESQL_USER="user"
export POLY_QUERY_POSTGRESQL_PASSWORD="password"
export POLY_QUERY_POSTGRESQL_DATABASE="database"

# Redis配置
export POLY_QUERY_REDIS_HOST="localhost"
export POLY_QUERY_REDIS_PORT="6379"
export POLY_QUERY_REDIS_PASSWORD="password"
export POLY_QUERY_REDIS_DB="0"

# MongoDB配置
export POLY_QUERY_MONGODB_HOST="localhost"
export POLY_QUERY_MONGODB_PORT="27017"
export POLY_QUERY_MONGODB_USERNAME="user"
export POLY_QUERY_MONGODB_PASSWORD="password"
export POLY_QUERY_MONGODB_DATABASE="database"
```

## 最佳实践

1. **使用增强版配置文件**：对于复杂环境，建议使用`config.enhanced.json`，它提供了更灵活的配置管理。

2. **环境隔离**：为不同环境（开发、测试、生产）创建不同的配置，避免配置混乱。

3. **敏感信息保护**：不要将密码等敏感信息直接写在MCP配置中，可以使用环境变量或配置文件。

4. **按需启用**：只启用需要的数据库，减少资源消耗。

5. **配置验证**：使用`--config-info`参数验证配置是否正确。

## 示例：完整的配置流程

1. 创建增强版配置文件`config.enhanced.json`

2. 在Claude Desktop的配置文件中添加MCP服务器：

```json
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
```

3. 重启Claude Desktop

4. 在对话中使用数据库查询功能

## 故障排除

1. **连接失败**：检查数据库配置是否正确，网络是否可达

2. **配置不生效**：检查配置文件路径和格式，使用`--config-info`查看当前配置

3. **权限问题**：确保数据库用户有足够的权限执行查询

4. **依赖问题**：确保安装了所有必要的数据库驱动

## 总结

通过这种配置整合方案，我们实现了：

1. **人性化配置**：支持多种配置方式，开发者可以选择最适合的方式

2. **按需配置**：可以根据环境和需求灵活调整数据库参数

3. **多层级结构**：支持环境、配置文件和默认值的多层级配置

4. **MCP兼容性**：确保配置能够正确被MCP连接程序识别和应用

这种方案既保持了配置的灵活性，又确保了使用的简便性，满足了不同场景下的配置需求。