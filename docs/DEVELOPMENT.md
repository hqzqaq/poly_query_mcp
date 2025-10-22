# Poly Query MCP 开发指南

## 项目结构

```
poly_query_mcp/
├── src/poly_query_mcp/          # 主源代码目录
│   ├── databases/               # 数据库连接模块
│   │   ├── base.py             # 数据库连接基类
│   │   ├── mysql_connection.py # MySQL连接实现
│   │   ├── postgresql_connection.py # PostgreSQL连接实现
│   │   ├── redis_connection.py # Redis连接实现
│   │   └── mongodb_connection.py # MongoDB连接实现
│   ├── utils/                  # 工具模块
│   │   ├── config.py           # 配置类定义
│   │   ├── config_manager.py   # 配置管理器
│   │   ├── logger.py           # 日志工具
│   │   └── exceptions.py       # 自定义异常
│   └── server.py               # MCP服务器主文件
├── docs/                       # 文档目录
│   ├── API.md                  # API文档
│   └── INSTALLATION.md         # 安装指南
├── main.py                     # 应用入口点
├── requirements.txt            # Python依赖
├── pyproject.toml             # 项目配置
└── config.example.json        # 配置示例
```

## 开发环境设置

1. 克隆项目
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

## 代码规范

1. 使用Python类型提示
2. 遵循PEP 8代码风格
3. 所有公共函数和类应有文档字符串
4. 使用适当的异常处理

## 添加新的数据库支持

1. 在`src/poly_query_mcp/databases/`目录下创建新的连接类
2. 继承自`DatabaseConnection`基类
3. 实现必要的方法：`connect`, `disconnect`, `execute_query`, `test_connection`
4. 在`server.py`中导入新的连接类
5. 在`get_connection`函数中添加对新数据库类型的支持
6. 在`handle_call_tool`函数中添加新的工具处理逻辑
7. 更新配置类以支持新数据库的配置参数

## 测试

1. 单元测试应放在`tests/`目录下
2. 测试文件命名模式：`test_*.py`
3. 使用pytest运行测试：
```bash
pytest tests/
```

## 发布流程

1. 更新版本号
2. 更新CHANGELOG.md
3. 运行测试确保所有测试通过
4. 创建发布标签
5. 构建并发布包