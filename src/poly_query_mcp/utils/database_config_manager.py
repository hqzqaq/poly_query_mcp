"""
数据库配置管理器
支持三种配置方式并按优先级处理：
1. 命令行参数直接传入 (最高优先级)
2. 普通配置文件 (中等优先级)  
3. 增强型多环境配置文件 (最低优先级)
"""

import json
import os
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """数据库配置数据类"""
    host: str = "localhost"
    port: int = 3306
    user: str = ""
    password: str = ""
    database: str = ""
    
    # PostgreSQL特有属性
    schema: str = "public"
    
    # Redis特有属性
    db: int = 0
    
    # MongoDB特有属性
    username: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "database": self.database
        }
        
        # 添加特定数据库类型的属性
        if self.schema != "public":
            result["schema"] = self.schema
        if self.db != 0:
            result["db"] = self.db
        if self.username:
            result["username"] = self.username
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatabaseConfig':
        """从字典创建配置对象"""
        # 处理不同数据库类型的特殊字段
        kwargs = {}
        
        # 通用字段
        for key in ["host", "port", "user", "password", "database"]:
            if key in data:
                kwargs[key] = data[key]
        
        # 特殊字段映射
        if "schema" in data:
            kwargs["schema"] = data["schema"]
        if "db" in data:
            kwargs["db"] = data["db"]
        if "username" in data:
            kwargs["username"] = data["username"]
            
        return cls(**kwargs)

@dataclass
class AllDatabaseConfigs:
    """所有数据库配置的容器"""
    mysql: Optional[DatabaseConfig] = None
    postgresql: Optional[DatabaseConfig] = None
    redis: Optional[DatabaseConfig] = None
    mongodb: Optional[DatabaseConfig] = None
    
    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        """转换为字典"""
        result = {}
        
        if self.mysql:
            result["mysql"] = self.mysql.to_dict()
        if self.postgresql:
            result["postgresql"] = self.postgresql.to_dict()
        if self.redis:
            result["redis"] = self.redis.to_dict()
        if self.mongodb:
            result["mongodb"] = self.mongodb.to_dict()
            
        return result

class DatabaseConfigManager:
    """数据库配置管理器"""
    
    def __init__(self, log_level: int = logging.INFO):
        """初始化配置管理器"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(log_level)
        
        # 配置来源
        self.cli_config = AllDatabaseConfigs()
        self.normal_config = AllDatabaseConfigs()
        self.enhanced_config = AllDatabaseConfigs()
        
        # 最终合并的配置
        self.final_config = AllDatabaseConfigs()
        
        # 配置加载状态
        self.config_sources = {
            "cli": {"loaded": False, "path": None},
            "normal": {"loaded": False, "path": None},
            "enhanced": {"loaded": False, "path": None}
        }
        
        # 增强配置的环境和配置文件信息
        self.current_environment = None
        self.current_profile = None
    
    def load_cli_config(self, args: Dict[str, Any]) -> None:
        """从命令行参数加载配置 (最高优先级)"""
        self.logger.info("开始加载命令行参数配置...")
        
        # MySQL配置
        if any(key.startswith('mysql_') for key in args):
            mysql_config = {}
            for key in ['host', 'port', 'user', 'password', 'database']:
                arg_key = f'mysql_{key}'
                if arg_key in args and args[arg_key] is not None:
                    mysql_config[key] = args[arg_key]
            
            if mysql_config:
                self.cli_config.mysql = DatabaseConfig.from_dict(mysql_config)
                self.logger.info(f"已加载MySQL命令行配置: {mysql_config}")
        
        # PostgreSQL配置
        if any(key.startswith('postgresql_') for key in args):
            postgresql_config = {}
            for key in ['host', 'port', 'user', 'password', 'database', 'schema']:
                arg_key = f'postgresql_{key}'
                if arg_key in args and args[arg_key] is not None:
                    postgresql_config[key] = args[arg_key]
            
            if postgresql_config:
                self.cli_config.postgresql = DatabaseConfig.from_dict(postgresql_config)
                self.logger.info(f"已加载PostgreSQL命令行配置: {postgresql_config}")
        
        # Redis配置
        if any(key.startswith('redis_') for key in args):
            redis_config = {}
            for key in ['host', 'port', 'password', 'db']:
                arg_key = f'redis_{key}'
                if arg_key in args and args[arg_key] is not None:
                    redis_config[key] = args[arg_key]
            
            if redis_config:
                self.cli_config.redis = DatabaseConfig.from_dict(redis_config)
                self.logger.info(f"已加载Redis命令行配置: {redis_config}")
        
        # MongoDB配置
        if any(key.startswith('mongodb_') for key in args):
            mongodb_config = {}
            for key in ['host', 'port', 'username', 'password', 'database']:
                arg_key = f'mongodb_{key}'
                if arg_key in args and args[arg_key] is not None:
                    mongodb_config[key] = args[arg_key]
            
            if mongodb_config:
                self.cli_config.mongodb = DatabaseConfig.from_dict(mongodb_config)
                self.logger.info(f"已加载MongoDB命令行配置: {mongodb_config}")
        
        self.config_sources["cli"]["loaded"] = True
        self.logger.info("命令行参数配置加载完成")
    
    def load_normal_config(self, config_path: str) -> None:
        """从普通配置文件加载配置 (中等优先级)"""
        self.logger.info(f"开始加载普通配置文件: {config_path}")
        
        try:
            if not os.path.exists(config_path):
                self.logger.warning(f"配置文件不存在: {config_path}")
                return
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # MySQL配置
            if 'mysql' in config_data:
                self.normal_config.mysql = DatabaseConfig.from_dict(config_data['mysql'])
                self.logger.info(f"已加载MySQL普通配置: {config_data['mysql']}")
            
            # PostgreSQL配置
            if 'postgresql' in config_data:
                self.normal_config.postgresql = DatabaseConfig.from_dict(config_data['postgresql'])
                self.logger.info(f"已加载PostgreSQL普通配置: {config_data['postgresql']}")
            
            # Redis配置
            if 'redis' in config_data:
                self.normal_config.redis = DatabaseConfig.from_dict(config_data['redis'])
                self.logger.info(f"已加载Redis普通配置: {config_data['redis']}")
            
            # MongoDB配置
            if 'mongodb' in config_data:
                self.normal_config.mongodb = DatabaseConfig.from_dict(config_data['mongodb'])
                self.logger.info(f"已加载MongoDB普通配置: {config_data['mongodb']}")
            
            self.config_sources["normal"]["loaded"] = True
            self.config_sources["normal"]["path"] = config_path
            self.logger.info("普通配置文件加载完成")
            
        except Exception as e:
            self.logger.error(f"加载普通配置文件失败: {str(e)}")
    
    def load_enhanced_config(self, config_path: str, environment: str = None, profile: str = None) -> None:
        """从增强型配置文件加载配置 (最低优先级)"""
        self.logger.info(f"开始加载增强型配置文件: {config_path}")
        
        try:
            if not os.path.exists(config_path):
                self.logger.warning(f"增强配置文件不存在: {config_path}")
                return
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 保存环境和配置文件信息
            self.current_environment = environment
            self.current_profile = profile
            
            # 获取基础配置
            base_config = config_data.get('default', {})
            
            # 应用环境配置
            if environment and 'environments' in config_data and environment in config_data['environments']:
                env_config = config_data['environments'][environment]
                # 深度合并环境配置到基础配置
                base_config = self._deep_merge(base_config, env_config)
                self.logger.info(f"已应用环境配置: {environment}")
            
            # 应用配置文件配置
            if profile and 'profiles' in config_data and profile in config_data['profiles']:
                profile_config = config_data['profiles'][profile]
                # 深度合并配置文件配置到基础配置
                base_config = self._deep_merge(base_config, profile_config)
                self.logger.info(f"已应用配置文件配置: {profile}")
            
            # 加载各种数据库配置
            if 'mysql' in base_config:
                self.enhanced_config.mysql = DatabaseConfig.from_dict(base_config['mysql'])
                self.logger.info(f"已加载MySQL增强配置: {base_config['mysql']}")
            
            if 'postgresql' in base_config:
                self.enhanced_config.postgresql = DatabaseConfig.from_dict(base_config['postgresql'])
                self.logger.info(f"已加载PostgreSQL增强配置: {base_config['postgresql']}")
            
            if 'redis' in base_config:
                self.enhanced_config.redis = DatabaseConfig.from_dict(base_config['redis'])
                self.logger.info(f"已加载Redis增强配置: {base_config['redis']}")
            
            if 'mongodb' in base_config:
                self.enhanced_config.mongodb = DatabaseConfig.from_dict(base_config['mongodb'])
                self.logger.info(f"已加载MongoDB增强配置: {base_config['mongodb']}")
            
            self.config_sources["enhanced"]["loaded"] = True
            self.config_sources["enhanced"]["path"] = config_path
            self.logger.info("增强型配置文件加载完成")
            
        except Exception as e:
            self.logger.error(f"加载增强型配置文件失败: {str(e)}")
    
    def merge_configs(self) -> None:
        """按优先级合并配置: 命令行 > 普通配置文件 > 增强配置文件"""
        self.logger.info("开始按优先级合并配置...")
        
        # 从最低优先级开始合并
        self.final_config = AllDatabaseConfigs()
        
        # 1. 合并增强配置 (最低优先级)
        if self.config_sources["enhanced"]["loaded"]:
            if self.enhanced_config.mysql:
                self.final_config.mysql = DatabaseConfig.from_dict(self.enhanced_config.mysql.to_dict())
            if self.enhanced_config.postgresql:
                self.final_config.postgresql = DatabaseConfig.from_dict(self.enhanced_config.postgresql.to_dict())
            if self.enhanced_config.redis:
                self.final_config.redis = DatabaseConfig.from_dict(self.enhanced_config.redis.to_dict())
            if self.enhanced_config.mongodb:
                self.final_config.mongodb = DatabaseConfig.from_dict(self.enhanced_config.mongodb.to_dict())
            
            self.logger.info("已合并增强型配置 (优先级: 低)")
        
        # 2. 合并普通配置 (中等优先级)
        if self.config_sources["normal"]["loaded"]:
            if self.normal_config.mysql:
                if self.final_config.mysql:
                    # 合并配置，普通配置覆盖增强配置
                    merged = self.final_config.mysql.to_dict()
                    merged.update(self.normal_config.mysql.to_dict())
                    self.final_config.mysql = DatabaseConfig.from_dict(merged)
                else:
                    self.final_config.mysql = DatabaseConfig.from_dict(self.normal_config.mysql.to_dict())
            
            if self.normal_config.postgresql:
                if self.final_config.postgresql:
                    merged = self.final_config.postgresql.to_dict()
                    merged.update(self.normal_config.postgresql.to_dict())
                    self.final_config.postgresql = DatabaseConfig.from_dict(merged)
                else:
                    self.final_config.postgresql = DatabaseConfig.from_dict(self.normal_config.postgresql.to_dict())
            
            if self.normal_config.redis:
                if self.final_config.redis:
                    merged = self.final_config.redis.to_dict()
                    merged.update(self.normal_config.redis.to_dict())
                    self.final_config.redis = DatabaseConfig.from_dict(merged)
                else:
                    self.final_config.redis = DatabaseConfig.from_dict(self.normal_config.redis.to_dict())
            
            if self.normal_config.mongodb:
                if self.final_config.mongodb:
                    merged = self.final_config.mongodb.to_dict()
                    merged.update(self.normal_config.mongodb.to_dict())
                    self.final_config.mongodb = DatabaseConfig.from_dict(merged)
                else:
                    self.final_config.mongodb = DatabaseConfig.from_dict(self.normal_config.mongodb.to_dict())
            
            self.logger.info("已合并普通配置文件 (优先级: 中)")
        
        # 3. 合并命令行配置 (最高优先级)
        if self.config_sources["cli"]["loaded"]:
            if self.cli_config.mysql:
                if self.final_config.mysql:
                    merged = self.final_config.mysql.to_dict()
                    merged.update(self.cli_config.mysql.to_dict())
                    self.final_config.mysql = DatabaseConfig.from_dict(merged)
                else:
                    self.final_config.mysql = DatabaseConfig.from_dict(self.cli_config.mysql.to_dict())
            
            if self.cli_config.postgresql:
                if self.final_config.postgresql:
                    merged = self.final_config.postgresql.to_dict()
                    merged.update(self.cli_config.postgresql.to_dict())
                    self.final_config.postgresql = DatabaseConfig.from_dict(merged)
                else:
                    self.final_config.postgresql = DatabaseConfig.from_dict(self.cli_config.postgresql.to_dict())
            
            if self.cli_config.redis:
                if self.final_config.redis:
                    merged = self.final_config.redis.to_dict()
                    merged.update(self.cli_config.redis.to_dict())
                    self.final_config.redis = DatabaseConfig.from_dict(merged)
                else:
                    self.final_config.redis = DatabaseConfig.from_dict(self.cli_config.redis.to_dict())
            
            if self.cli_config.mongodb:
                if self.final_config.mongodb:
                    merged = self.final_config.mongodb.to_dict()
                    merged.update(self.cli_config.mongodb.to_dict())
                    self.final_config.mongodb = DatabaseConfig.from_dict(merged)
                else:
                    self.final_config.mongodb = DatabaseConfig.from_dict(self.cli_config.mongodb.to_dict())
            
            self.logger.info("已合并命令行配置 (优先级: 高)")
        
        self.logger.info("配置合并完成")
        self._log_final_config()
    
    def get_final_config(self) -> AllDatabaseConfigs:
        """获取最终合并后的配置"""
        return self.final_config
    
    def get_mysql_config(self) -> Optional[DatabaseConfig]:
        """获取MySQL配置"""
        return self.final_config.mysql
    
    def get_postgresql_config(self) -> Optional[DatabaseConfig]:
        """获取PostgreSQL配置"""
        return self.final_config.postgresql
    
    def get_redis_config(self) -> Optional[DatabaseConfig]:
        """获取Redis配置"""
        return self.final_config.redis
    
    def get_mongodb_config(self) -> Optional[DatabaseConfig]:
        """获取MongoDB配置"""
        return self.final_config.mongodb
    
    def get_config_sources_info(self) -> Dict[str, Any]:
        """获取配置来源信息"""
        return {
            "sources": self.config_sources,
            "environment": self.current_environment,
            "profile": self.current_profile
        }
    
    def load_and_merge_config(self, command_line_args: List[str], normal_config_file: str = None, enhanced_config_file: str = None, environment: str = None) -> Dict[str, Any]:
        """
        加载并合并配置的便捷方法
        
        Args:
            command_line_args: 命令行参数列表
            normal_config_file: 普通配置文件路径
            enhanced_config_file: 增强型配置文件路径
            environment: 环境名称
            
        Returns:
            合并后的配置字典
        """
        # 解析命令行参数
        from src.poly_query_mcp.utils.enhanced_config_manager import parse_config_args
        cli_args = parse_config_args(command_line_args)
        
        # 加载命令行配置
        if cli_args.get("config_overrides"):
            # 直接使用config_overrides中的配置
            for db_type, config in cli_args["config_overrides"].items():
                if db_type == "mysql" and config:
                    self.cli_config.mysql = DatabaseConfig.from_dict(config)
                    self.logger.info(f"已加载MySQL命令行配置: {config}")
                elif db_type == "postgresql" and config:
                    self.cli_config.postgresql = DatabaseConfig.from_dict(config)
                    self.logger.info(f"已加载PostgreSQL命令行配置: {config}")
                elif db_type == "redis" and config:
                    self.cli_config.redis = DatabaseConfig.from_dict(config)
                    self.logger.info(f"已加载Redis命令行配置: {config}")
                elif db_type == "mongodb" and config:
                    self.cli_config.mongodb = DatabaseConfig.from_dict(config)
                    self.logger.info(f"已加载MongoDB命令行配置: {config}")
            
            self.config_sources["cli"]["loaded"] = True
            self.logger.info("命令行参数配置加载完成")
        
        # 加载普通配置文件
        if normal_config_file:
            self.load_normal_config(normal_config_file)
        
        # 加载增强型配置文件
        if enhanced_config_file:
            self.load_enhanced_config(enhanced_config_file, environment)
        
        # 合并配置
        self.merge_configs()
        
        # 返回合并后的配置
        return self.get_final_config().to_dict()
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并两个字典"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result
    
    def _log_final_config(self) -> None:
        """记录最终配置信息"""
        self.logger.info("最终生效的配置:")
        
        if self.final_config.mysql:
            self.logger.info(f"  MySQL: {self.final_config.mysql.host}:{self.final_config.mysql.port}/{self.final_config.mysql.database} (用户: {self.final_config.mysql.user})")
        
        if self.final_config.postgresql:
            self.logger.info(f"  PostgreSQL: {self.final_config.postgresql.host}:{self.final_config.postgresql.port}/{self.final_config.postgresql.database} (模式: {self.final_config.postgresql.schema}, 用户: {self.final_config.postgresql.user})")
        
        if self.final_config.redis:
            self.logger.info(f"  Redis: {self.final_config.redis.host}:{self.final_config.redis.port}/{self.final_config.redis.db} (密码: {'已设置' if self.final_config.redis.password else '未设置'})")
        
        if self.final_config.mongodb:
            self.logger.info(f"  MongoDB: {self.final_config.mongodb.host}:{self.final_config.mongodb.port}/{self.final_config.mongodb.database} (用户: {self.final_config.mongodb.username})")
    
    def log_connection_error(self, db_type: str, error: Exception) -> None:
        """记录数据库连接错误和配置信息"""
        config = None
        if db_type.lower() == "mysql":
            config = self.final_config.mysql
        elif db_type.lower() == "postgresql":
            config = self.final_config.postgresql
        elif db_type.lower() == "redis":
            config = self.final_config.redis
        elif db_type.lower() == "mongodb":
            config = self.final_config.mongodb
        
        if config:
            self.logger.error(f"{db_type} 数据库连接失败:")
            self.logger.error(f"  错误信息: {str(error)}")
            self.logger.error(f"  连接配置: {config.to_dict()}")
            
            # 记录配置来源
            sources_info = []
            if self.config_sources["cli"]["loaded"]:
                sources_info.append("命令行参数")
            if self.config_sources["normal"]["loaded"]:
                sources_info.append(f"普通配置文件({self.config_sources['normal']['path']})")
            if self.config_sources["enhanced"]["loaded"]:
                env_info = f", 环境: {self.current_environment}" if self.current_environment else ""
                profile_info = f", 配置文件: {self.current_profile}" if self.current_profile else ""
                sources_info.append(f"增强配置文件({self.config_sources['enhanced']['path']}{env_info}{profile_info})")
            
            self.logger.error(f"  配置来源: {' > '.join(sources_info)}")
        else:
            self.logger.error(f"{db_type} 数据库连接失败，但没有找到相关配置")
            self.logger.error(f"  错误信息: {str(error)}")