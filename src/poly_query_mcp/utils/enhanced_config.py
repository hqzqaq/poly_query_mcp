"""
增强版配置管理模块
"""

import os
import re
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


def substitute_env_vars(value: str) -> str:
    """替换字符串中的环境变量"""
    if not isinstance(value, str):
        return value
    
    # 匹配 ${VAR_NAME} 或 $VAR_NAME 格式的环境变量
    pattern = r'\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)'
    
    def replacer(match):
        var_name = match.group(1) or match.group(2)
        return os.getenv(var_name, match.group(0))
    
    return re.sub(pattern, replacer, value)


class DatabaseConfig(BaseModel):
    """数据库配置基类"""
    host: str = Field(..., description="数据库主机地址")
    port: int = Field(..., description="数据库端口")
    username: Optional[str] = Field(None, description="用户名")
    user: Optional[str] = Field(None, description="用户名（别名）")
    password: Optional[str] = Field(None, description="密码")
    database: Optional[str] = Field(None, description="数据库名")
    
    def get_username(self) -> Optional[str]:
        """获取用户名，支持user和username两种字段"""
        return self.username or self.user
    
    def get_password(self) -> Optional[str]:
        """获取密码，支持环境变量替换"""
        if self.password:
            return substitute_env_vars(self.password)
        return None
    
    class Config:
        extra = "allow"


class MySQLConfig(DatabaseConfig):
    """MySQL数据库配置"""
    port: int = Field(3306, description="MySQL默认端口")
    charset: str = Field("utf8mb4", description="字符集")


class PostgreSQLConfig(DatabaseConfig):
    """PostgreSQL数据库配置"""
    port: int = Field(5432, description="PostgreSQL默认端口")


class RedisConfig(DatabaseConfig):
    """Redis数据库配置"""
    port: int = Field(6379, description="Redis默认端口")
    db: int = Field(0, description="Redis数据库索引")


class MongoDBConfig(DatabaseConfig):
    """MongoDB数据库配置"""
    port: int = Field(27017, description="MongoDB默认端口")


class EnvironmentConfig(BaseModel):
    """环境配置"""
    mysql: Optional[MySQLConfig] = None
    postgresql: Optional[PostgreSQLConfig] = None
    redis: Optional[RedisConfig] = None
    mongodb: Optional[MongoDBConfig] = None
    
    class Config:
        extra = "allow"


class ProfileConfig(BaseModel):
    """配置文件"""
    environment: str = Field(..., description="环境名称")
    databases: Optional[List[str]] = Field(None, description="启用的数据库列表")
    description: Optional[str] = Field(None, description="配置描述")
    
    class Config:
        extra = "allow"


class DefaultConfig(BaseModel):
    """默认配置"""
    environment: str = Field("development", description="默认环境")
    log_level: str = Field("INFO", description="日志级别")
    connection_pool_size: int = Field(5, description="连接池大小")
    connection_timeout: int = Field(30, description="连接超时时间(秒)")
    
    class Config:
        extra = "allow"


class EnhancedAppConfig(BaseSettings):
    """增强版应用配置"""
    environments: Dict[str, EnvironmentConfig] = Field(default_factory=dict)
    profiles: Dict[str, ProfileConfig] = Field(default_factory=dict)
    defaults: DefaultConfig = Field(default_factory=DefaultConfig)
    
    # 当前激活的环境和配置文件
    current_environment: str = Field("development")
    current_profile: Optional[str] = None
    
    # 当前生效的数据库配置
    mysql: Optional[MySQLConfig] = None
    postgresql: Optional[PostgreSQLConfig] = None
    redis: Optional[RedisConfig] = None
    mongodb: Optional[MongoDBConfig] = None
    
    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
        case_sensitive = False
    
    def activate_profile(self, profile_name: str) -> bool:
        """激活指定的配置文件"""
        if profile_name not in self.profiles:
            return False
        
        profile = self.profiles[profile_name]
        self.current_profile = profile_name
        self.current_environment = profile.environment
        
        # 应用环境配置
        self._apply_environment_config(profile.environment, profile.databases)
        return True
    
    def activate_environment(self, environment_name: str, databases: Optional[List[str]] = None) -> bool:
        """激活指定的环境"""
        if environment_name not in self.environments:
            return False
        
        self.current_environment = environment_name
        self.current_profile = None
        
        # 应用环境配置
        self._apply_environment_config(environment_name, databases)
        return True
    
    def _apply_environment_config(self, environment_name: str, databases: Optional[List[str]] = None) -> None:
        """应用环境配置"""
        if environment_name not in self.environments:
            return
        
        env_config = self.environments[environment_name]
        
        # 如果指定了数据库列表，只应用指定的数据库配置
        if databases:
            if "mysql" in databases and env_config.mysql:
                self.mysql = env_config.mysql
            if "postgresql" in databases and env_config.postgresql:
                self.postgresql = env_config.postgresql
            if "redis" in databases and env_config.redis:
                self.redis = env_config.redis
            if "mongodb" in databases and env_config.mongodb:
                self.mongodb = env_config.mongodb
        else:
            # 应用所有数据库配置
            self.mysql = env_config.mysql
            self.postgresql = env_config.postgresql
            self.redis = env_config.redis
            self.mongodb = env_config.mongodb
    
    @classmethod
    def load_from_dict(cls, config_dict: Dict[str, Any]) -> "EnhancedAppConfig":
        """从字典加载配置"""
        # 解析环境配置
        environments = {}
        if "environments" in config_dict:
            for env_name, env_data in config_dict["environments"].items():
                environments[env_name] = EnvironmentConfig(**env_data)
        
        # 解析配置文件
        profiles = {}
        if "profiles" in config_dict:
            for profile_name, profile_data in config_dict["profiles"].items():
                profiles[profile_name] = ProfileConfig(**profile_data)
        
        # 解析默认配置
        defaults = DefaultConfig()
        if "defaults" in config_dict:
            defaults = DefaultConfig(**config_dict["defaults"])
        
        # 创建配置对象
        config = cls(
            environments=environments,
            profiles=profiles,
            defaults=defaults
        )
        
        # 激活默认环境
        config.activate_environment(defaults.environment)
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "environments": {name: env.dict() for name, env in self.environments.items()},
            "profiles": {name: profile.dict() for name, profile in self.profiles.items()},
            "defaults": self.defaults.dict(),
            "current_environment": self.current_environment,
            "current_profile": self.current_profile
        }
        
        # 添加当前激活的数据库配置
        if self.mysql:
            result["mysql"] = self.mysql.dict()
        if self.postgresql:
            result["postgresql"] = self.postgresql.dict()
        if self.redis:
            result["redis"] = self.redis.dict()
        if self.mongodb:
            result["mongodb"] = self.mongodb.dict()
        
        return result