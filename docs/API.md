# API参考文档

本文档详细描述了Poly Query MCP工具提供的所有API接口和参数。

## 概述

Poly Query MCP提供了以下工具：

1. `query_mysql` - MySQL数据库查询
2. `query_postgresql` - PostgreSQL数据库查询
3. `query_redis` - Redis命令执行
4. `query_mongodb` - MongoDB数据库查询
5. `test_connection` - 数据库连接测试

## 通用响应格式

所有查询工具的响应都遵循以下JSON格式：

```json
{
  "success": true|false,
  "data": [...],
  "columns": [...],
  "message": "操作结果描述",
  "execution_time": 0.123
}
```

- `success`: 操作是否成功
- `data`: 查询结果数据（数组格式）
- `columns`: 结果列名（仅SQL查询）
- `message`: 操作结果描述
- `execution_time`: 查询执行时间（秒）

## 1. query_mysql

查询MySQL数据库。

### 参数

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| query | string | 是 | SQL查询语句 |
| params | object | 否 | 查询参数字典，用于参数化查询 |

### 示例

#### 基本查询

```json
{
  "query": "SELECT * FROM users LIMIT 10"
}
```

#### 参数化查询

```json
{
  "query": "SELECT * FROM users WHERE age > ? AND status = ?",
  "params": {
    "age": 18,
    "status": "active"
  }
}
```

#### 插入数据

```json
{
  "query": "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
  "params": {
    "name": "张三",
    "email": "zhangsan@example.com",
    "age": 25
  }
}
```

### 支持的SQL语句

- SELECT
- INSERT
- UPDATE
- DELETE
- SHOW TABLES
- DESCRIBE table_name
- EXPLAIN query

### 响应示例

```json
{
  "success": true,
  "data": [
    {"id": 1, "name": "张三", "email": "zhangsan@example.com", "age": 25},
    {"id": 2, "name": "李四", "email": "lisi@example.com", "age": 30}
  ],
  "columns": ["id", "name", "email", "age"],
  "message": "查询成功，返回2条记录",
  "execution_time": 0.045
}
```

## 2. query_postgresql

查询PostgreSQL数据库。

### 参数

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| query | string | 是 | SQL查询语句 |
| params | object | 否 | 查询参数字典，用于参数化查询 |

### 配置参数

除了查询参数外，PostgreSQL连接还支持以下配置参数：

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| host | string | localhost | 数据库主机地址 |
| port | integer | 5432 | 数据库端口 |
| database | string | - | 数据库名称 |
| username | string | - | 用户名 |
| password | string | - | 密码 |
| schema | string | public | 数据库模式名称 |

#### Schema配置说明

PostgreSQL支持多个schema（模式），默认使用public schema。您可以通过以下方式指定schema：

1. **配置文件**：
```json
{
  "postgresql": {
    "host": "localhost",
    "port": 5432,
    "database": "mydb",
    "username": "user",
    "password": "pass",
    "schema": "custom_schema"
  }
}
```

2. **命令行参数**：
```bash
python main.py --postgresql-schema custom_schema
```

3. **环境变量**：
```bash
export POSTGRESQL_SCHEMA=custom_schema
```

当指定schema后，所有查询将默认在该schema中执行，无需在SQL语句中显式指定schema名称。

### 示例

#### 基本查询

```json
{
  "query": "SELECT * FROM products LIMIT 10"
}
```

#### 参数化查询

```json
{
  "query": "SELECT * FROM products WHERE category = %s AND price < %s",
  "params": {
    "category": "electronics",
    "price": 1000
  }
}
```

#### 使用PostgreSQL特有功能

```json
{
  "query": "SELECT * FROM products WHERE tags @> ARRAY['popular']::text[]"
}
```

### 支持的SQL语句

- 所有标准SQL语句
- PostgreSQL扩展语法
- \d 命令（描述表结构）

### 响应示例

```json
{
  "success": true,
  "data": [
    {"id": 1, "name": "智能手机", "category": "electronics", "price": 899.99}
  ],
  "columns": ["id", "name", "category", "price"],
  "message": "查询成功，返回1条记录",
  "execution_time": 0.032
}
```

## 3. query_redis

执行Redis命令。

### 参数

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| command | string | 是 | Redis命令 |
| args | array | 否 | 命令参数列表 |

### 示例

#### 基本操作

```json
{
  "command": "GET",
  "args": ["user:123"]
}
```

#### 设置键值

```json
{
  "command": "SET",
  "args": ["user:123", "{\"name\":\"张三\",\"age\":25}"]
}
```

#### 哈希操作

```json
{
  "command": "HGETALL",
  "args": ["user:123"]
}
```

#### 列表操作

```json
{
  "command": "LRANGE",
  "args": ["messages", 0, 10]
}
```

#### 集合操作

```json
{
  "command": "SMEMBERS",
  "args": ["tags:article:456"]
}
```

### 支持的Redis命令

- 字符串命令：GET, SET, MGET, MSET, INCR, DECR等
- 哈希命令：HGET, HSET, HGETALL, HMGET, HMSET等
- 列表命令：LINDEX, LLEN, LPOP, LPUSH, LRANGE等
- 集合命令：SADD, SMEMBERS, SREM, SCARD等
- 有序集合命令：ZADD, ZRANGE, ZREM, ZCARD等
- 服务器命令：INFO, CONFIG GET, DBSIZE等

### 响应示例

```json
{
  "success": true,
  "data": "{\"name\":\"张三\",\"age\":25}",
  "message": "Redis命令执行成功",
  "execution_time": 0.005
}
```

## 4. query_mongodb

查询MongoDB数据库。

### 参数

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| collection | string | 是 | 集合名称 |
| operation | string | 是 | 操作类型 |
| filter | object | 否 | 查询过滤器 |
| pipeline | array | 否 | 聚合管道（用于aggregate操作） |
| options | object | 否 | 查询选项（如limit, skip等） |

### 支持的操作类型

- `find` - 查找多个文档
- `findOne` - 查找单个文档
- `count` - 计数文档
- `aggregate` - 聚合查询
- `insertOne` - 插入单个文档
- `insertMany` - 插入多个文档
- `updateOne` - 更新单个文档
- `updateMany` - 更新多个文档
- `deleteOne` - 删除单个文档
- `deleteMany` - 删除多个文档

### 示例

#### 查找文档

```json
{
  "collection": "users",
  "operation": "find",
  "filter": {"status": "active"},
  "options": {"limit": 10}
}
```

#### 查找单个文档

```json
{
  "collection": "users",
  "operation": "findOne",
  "filter": {"email": "zhangsan@example.com"}
}
```

#### 聚合查询

```json
{
  "collection": "orders",
  "operation": "aggregate",
  "pipeline": [
    {"$match": {"status": "completed"}},
    {"$group": {"_id": "$product", "total": {"$sum": "$amount"}}},
    {"$sort": {"total": -1}}
  ]
}
```

#### 插入文档

```json
{
  "collection": "users",
  "operation": "insertOne",
  "document": {
    "name": "王五",
    "email": "wangwu@example.com",
    "age": 28
  }
}
```

#### 更新文档

```json
{
  "collection": "users",
  "operation": "updateOne",
  "filter": {"email": "zhangsan@example.com"},
  "update": {"$set": {"age": 26}}
}
```

### 响应示例

```json
{
  "success": true,
  "data": [
    {"_id": "64a7b8c9d1e2f3g4h5i6j7k8", "name": "张三", "email": "zhangsan@example.com", "age": 25, "status": "active"},
    {"_id": "64a7b8c9d1e2f3g4h5i6j7k9", "name": "李四", "email": "lisi@example.com", "age": 30, "status": "active"}
  ],
  "message": "MongoDB查询成功，返回2条记录",
  "execution_time": 0.023
}
```

## 5. test_connection

测试数据库连接。

### 参数

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| db_type | string | 是 | 数据库类型（mysql, postgresql, redis, mongodb） |

### 示例

```json
{
  "db_type": "mysql"
}
```

### 响应示例

```json
{
  "success": true,
  "message": "MySQL连接测试: 成功",
  "execution_time": 0.012
}
```

## 错误处理

当操作失败时，API会返回错误信息：

```json
{
  "success": false,
  "error": "错误类型",
  "message": "详细错误描述",
  "execution_time": 0.001
}
```

### 常见错误类型

- `ValidationError`: 参数验证错误
- `DatabaseConnectionError`: 数据库连接错误
- `DatabaseQueryError`: 数据库查询错误
- `ConfigurationError`: 配置错误

## 限制

1. 查询结果大小限制：默认最大返回1000条记录
2. 查询超时：默认30秒
3. 参数化查询：仅支持SQL数据库（MySQL和PostgreSQL）
4. MongoDB聚合管道：最大管道长度为100

## 最佳实践

1. 使用参数化查询防止SQL注入
2. 限制查询结果集大小
3. 为复杂查询添加适当的索引
4. 定期检查连接状态
5. 使用适当的错误处理机制