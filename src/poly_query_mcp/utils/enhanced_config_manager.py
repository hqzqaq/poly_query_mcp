"""
增强版配置管理器
"""

import os
import json
import logging
import argparse
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dotenv import load_dotenv

from .config import AppConfig
from .enhanced_config import EnhancedAppConfig

logger = logging.getLogger(__name__)


class EnhancedConfigManager:
    """增强版配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or os.path.join(os.path.dirname(__file__), "config.json")
        self.enhanced_config_file = os.path.join(
            os.path.dirname(self.config_file), 
            "config.enhanced.json"
        )
        self.config = None
        self.use_enhanced = False
        self.load_config()
    
    def load_config(self, 
                   profile: Optional[str] = None, 
                   environment: Optional[str] = None,
                   databases: Optional[List[str]] = None,
                   config_overrides: Optional[Dict[str, Any]] = None) -> None:
        """加载配置文件"""
        try:
            # 首先加载环境变量
            load_dotenv()
            
            # 检查增强版配置文件是否存在
            if os.path.exists(self.enhanced_config_file):
                self._load_enhanced_config(profile, environment, databases, config_overrides)
                self.use_enhanced = True
                logger.info(f"使用增强版配置文件: {self.enhanced_config_file}")
            elif os.path.exists(self.config_file):
                self._load_legacy_config(config_overrides)
                self.use_enhanced = False
                logger.info(f"使用传统配置文件: {self.config_file}")
            else:
                logger.warning(f"配置文件不存在，使用默认配置")
                self.config = self._get_default_config()
                self.use_enhanced = False
                self.save_config()  # 保存默认配置
        
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            logger.info("使用默认配置")
            self.config = self._get_default_config()
            self.use_enhanced = False
    
    def _load_enhanced_config(self, 
                            profile: Optional[str] = None, 
                            environment: Optional[str] = None,
                            databases: Optional[List[str]] = None,
                            config_overrides: Optional[Dict[str, Any]] = None) -> None:
        """加载增强版配置"""
        # 加载配置文件
        with open(self.enhanced_config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 使用EnhancedAppConfig加载配置
        self.config = EnhancedAppConfig.load_from_dict(config_data)
        
        # 激活指定的配置文件或环境
        if profile:
            success = self.config.activate_profile(profile)
            if not success:
                logger.warning(f"未找到配置文件: {profile}")
                # 尝试使用默认环境
                self.config.activate_environment(self.config.defaults.environment, databases)
        elif environment:
            success = self.config.activate_environment(environment, databases)
            if not success:
                logger.warning(f"未找到环境: {environment}")
                # 使用默认环境
                self.config.activate_environment(self.config.defaults.environment, databases)
        else:
            # 使用默认环境
            self.config.activate_environment(self.config.defaults.environment, databases)
        
        # 应用配置覆盖
        if config_overrides:
            self._apply_config_overrides(config_overrides)
    
    def _load_legacy_config(self, config_overrides: Optional[Dict[str, Any]] = None) -> None:
        """加载传统配置"""
        # 加载配置文件
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 使用AppConfig加载配置
        self.config = AppConfig.load_from_dict(config_data)
        
        # 应用配置覆盖
        if config_overrides:
            self._apply_config_overrides(config_overrides)
    
    def _apply_config_overrides(self, config_overrides: Dict[str, Any]) -> None:
        """应用配置覆盖"""
        try:
            if self.use_enhanced:
                # 对于增强版配置，直接更新当前激活的数据库配置
                for db_type, db_config in config_overrides.items():
                    if hasattr(self.config, db_type) and db_config:
                        if db_type == "mysql" and self.config.mysql:
                            for key, value in db_config.items():
                                setattr(self.config.mysql, key, value)
                        elif db_type == "postgresql" and self.config.postgresql:
                            for key, value in db_config.items():
                                setattr(self.config.postgresql, key, value)
                        elif db_type == "redis" and self.config.redis:
                            for key, value in db_config.items():
                                setattr(self.config.redis, key, value)
                        elif db_type == "mongodb" and self.config.mongodb:
                            for key, value in db_config.items():
                                setattr(self.config.mongodb, key, value)
            else:
                # 对于传统配置，创建新的配置对象
                current_config_dict = self.config.to_dict()
                for db_type, db_config in config_overrides.items():
                    if db_type in current_config_dict and db_config:
                        current_config_dict[db_type].update(db_config)
                
                self.config = AppConfig.load_from_dict(current_config_dict)
        except Exception as e:
            logger.error(f"应用配置覆盖失败: {str(e)}")
    
    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            if self.use_enhanced:
                return self._save_enhanced_config()
            else:
                return self._save_legacy_config()
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")
            return False
    
    def _save_enhanced_config(self) -> bool:
        """保存增强版配置"""
        # 确保目录存在
        os.makedirs(os.path.dirname(self.enhanced_config_file), exist_ok=True)
        
        # 将配置转换为字典
        config_dict = self.config.to_dict()
        
        # 保存到文件
        with open(self.enhanced_config_file, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"配置已保存到: {self.enhanced_config_file}")
        return True
    
    def _save_legacy_config(self) -> bool:
        """保存传统配置"""
        # 确保目录存在
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        # 将配置转换为字典
        config_dict = self.config.to_dict()
        
        # 保存到文件
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"配置已保存到: {self.config_file}")
        return True
    
    def get_config(self):
        """获取配置对象"""
        return self.config
    
    def is_enhanced_config(self) -> bool:
        """是否使用增强版配置"""
        return self.use_enhanced
    
    def list_environments(self) -> List[str]:
        """列出所有可用环境"""
        if self.use_enhanced:
            return list(self.config.environments.keys())
        return []
    
    def list_profiles(self) -> List[str]:
        """列出所有可用配置文件"""
        if self.use_enhanced:
            return list(self.config.profiles.keys())
        return []
    
    def get_current_environment(self) -> str:
        """获取当前激活的环境"""
        if self.use_enhanced:
            return self.config.current_environment
        return "default"
    
    def get_current_profile(self) -> Optional[str]:
        """获取当前激活的配置文件"""
        if self.use_enhanced:
            return self.config.current_profile
        return None
    
    def _get_default_config(self) -> AppConfig:
        """获取默认配置"""
        return AppConfig(
            mysql={
                "host": os.getenv("MYSQL_HOST", "localhost"),
                "port": int(os.getenv("MYSQL_PORT", "3306")),
                "user": os.getenv("MYSQL_USER", "root"),
                "password": os.getenv("MYSQL_PASSWORD", ""),
                "database": os.getenv("MYSQL_DATABASE", "")
            },
            postgresql={
                "host": os.getenv("POSTGRESQL_HOST", "localhost"),
                "port": int(os.getenv("POSTGRESQL_PORT", "5432")),
                "user": os.getenv("POSTGRESQL_USER", "postgres"),
                "password": os.getenv("POSTGRESQL_PASSWORD", ""),
                "database": os.getenv("POSTGRESQL_DATABASE", ""),
                "schema": os.getenv("POSTGRESQL_SCHEMA", "public")
            },
            redis={
                "host": os.getenv("REDIS_HOST", "localhost"),
                "port": int(os.getenv("REDIS_PORT", "6379")),
                "db": int(os.getenv("REDIS_DB", "0")),
                "password": os.getenv("REDIS_PASSWORD", "")
            },
            mongodb={
                "host": os.getenv("MONGODB_HOST", "localhost"),
                "port": int(os.getenv("MONGODB_PORT", "27017")),
                "username": os.getenv("MONGODB_USERNAME", ""),
                "password": os.getenv("MONGODB_PASSWORD", ""),
                "database": os.getenv("MONGODB_DATABASE", "")
            }
        )
    
    def create_enhanced_sample_config(self, file_path: str) -> bool:
        """创建增强版示例配置文件"""
        try:
            sample_config = {
                "environments": {
                    "development": {
                        "mysql": {
                            "host": "localhost",
                            "port": 3306,
                            "user": "root",
                            "password": "dev_mysql_password",
                            "database": "dev_db"
                        },
                        "postgresql": {
                        "host": "localhost",
                        "port": 5432,
                        "user": "postgres",
                        "password": "dev_postgresql_password",
                        "database": "dev_db",
                        "schema": "public"
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
                            "database": "production_db"
                        },
                        "postgresql": {
                        "host": "prod-postgresql.example.com",
                        "port": 5432,
                        "user": "app_user",
                        "password": "${POSTGRESQL_PROD_PASSWORD}",
                        "database": "production_db",
                        "schema": "public"
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
            
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 保存示例配置
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(sample_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"增强版示例配置已创建: {file_path}")
            return True
        except Exception as e:
            logger.error(f"创建增强版示例配置文件失败: {str(e)}")
            return False


def parse_config_args(args: Optional[List[str]] = None) -> Dict[str, Any]:
    """解析配置相关的命令行参数"""
    parser = argparse.ArgumentParser(add_help=False)
    
    # 配置相关参数
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--profile', type=str, help='配置文件名称')
    parser.add_argument('--environment', type=str, help='环境名称')
    parser.add_argument('--databases', type=str, help='启用的数据库列表，用逗号分隔')
    
    # 数据库配置覆盖参数
    parser.add_argument('--mysql-host', type=str, help='MySQL主机地址')
    parser.add_argument('--mysql-port', type=int, help='MySQL端口')
    parser.add_argument('--mysql-user', type=str, help='MySQL用户名')
    parser.add_argument('--mysql-password', type=str, help='MySQL密码')
    parser.add_argument('--mysql-database', type=str, help='MySQL数据库名')
    
    parser.add_argument('--postgresql-host', type=str, help='PostgreSQL主机地址')
    parser.add_argument('--postgresql-port', type=int, help='PostgreSQL端口')
    parser.add_argument('--postgresql-user', type=str, help='PostgreSQL用户名')
    parser.add_argument('--postgresql-password', type=str, help='PostgreSQL密码')
    parser.add_argument('--postgresql-database', type=str, help='PostgreSQL数据库名')
    parser.add_argument('--postgresql-schema', type=str, help='PostgreSQL模式名')
    
    parser.add_argument('--redis-host', type=str, help='Redis主机地址')
    parser.add_argument('--redis-port', type=int, help='Redis端口')
    parser.add_argument('--redis-password', type=str, help='Redis密码')
    parser.add_argument('--redis-db', type=int, help='Redis数据库索引')
    
    parser.add_argument('--mongodb-host', type=str, help='MongoDB主机地址')
    parser.add_argument('--mongodb-port', type=int, help='MongoDB端口')
    parser.add_argument('--mongodb-username', type=str, help='MongoDB用户名')
    parser.add_argument('--mongodb-password', type=str, help='MongoDB密码')
    parser.add_argument('--mongodb-database', type=str, help='MongoDB数据库名')
    
    # 解析参数
    if args is None:
        parsed_args = parser.parse_args()
    else:
        parsed_args = parser.parse_args(args)
    
    # 打印调试信息
    print(f"调试信息 - argparse解析结果:")
    print(f"  mysql_host: {parsed_args.mysql_host}")
    print(f"  mysql_port: {parsed_args.mysql_port}")
    print(f"  mysql_user: {parsed_args.mysql_user}")
    print(f"  mysql_password: {parsed_args.mysql_password}")
    print(f"  mysql_database: {parsed_args.mysql_database}")
    
    # 构建配置覆盖字典
    config_overrides = {}
    
    # MySQL配置覆盖
    mysql_overrides = {}
    if parsed_args.mysql_host:
        mysql_overrides["host"] = parsed_args.mysql_host
    if parsed_args.mysql_port:
        mysql_overrides["port"] = parsed_args.mysql_port
    if parsed_args.mysql_user:
        mysql_overrides["user"] = parsed_args.mysql_user
    if parsed_args.mysql_password:
        mysql_overrides["password"] = parsed_args.mysql_password
    if parsed_args.mysql_database:
        mysql_overrides["database"] = parsed_args.mysql_database
    
    if mysql_overrides:
        config_overrides["mysql"] = mysql_overrides
    
    # PostgreSQL配置覆盖
    postgresql_overrides = {}
    if parsed_args.postgresql_host:
        postgresql_overrides["host"] = parsed_args.postgresql_host
    if parsed_args.postgresql_port:
        postgresql_overrides["port"] = parsed_args.postgresql_port
    if parsed_args.postgresql_user:
        postgresql_overrides["user"] = parsed_args.postgresql_user
    if parsed_args.postgresql_password:
        postgresql_overrides["password"] = parsed_args.postgresql_password
    if parsed_args.postgresql_database:
        postgresql_overrides["database"] = parsed_args.postgresql_database
    if parsed_args.postgresql_schema:
        postgresql_overrides["schema"] = parsed_args.postgresql_schema
    
    if postgresql_overrides:
        config_overrides["postgresql"] = postgresql_overrides
    
    # Redis配置覆盖
    redis_overrides = {}
    if parsed_args.redis_host:
        redis_overrides["host"] = parsed_args.redis_host
    if parsed_args.redis_port:
        redis_overrides["port"] = parsed_args.redis_port
    if parsed_args.redis_password:
        redis_overrides["password"] = parsed_args.redis_password
    if parsed_args.redis_db:
        redis_overrides["db"] = parsed_args.redis_db
    
    if redis_overrides:
        config_overrides["redis"] = redis_overrides
    
    # MongoDB配置覆盖
    mongodb_overrides = {}
    if parsed_args.mongodb_host:
        mongodb_overrides["host"] = parsed_args.mongodb_host
    if parsed_args.mongodb_port:
        mongodb_overrides["port"] = parsed_args.mongodb_port
    if parsed_args.mongodb_username:
        mongodb_overrides["username"] = parsed_args.mongodb_username
    if parsed_args.mongodb_password:
        mongodb_overrides["password"] = parsed_args.mongodb_password
    if parsed_args.mongodb_database:
        mongodb_overrides["database"] = parsed_args.mongodb_database
    
    if mongodb_overrides:
        config_overrides["mongodb"] = mongodb_overrides
    
    # 解析数据库列表
    databases = None
    if parsed_args.databases:
        databases = [db.strip() for db in parsed_args.databases.split(',')]
    
    return {
        "config_file": parsed_args.config,
        "profile": parsed_args.profile,
        "environment": parsed_args.environment,
        "databases": databases,
        "config_overrides": config_overrides
    }