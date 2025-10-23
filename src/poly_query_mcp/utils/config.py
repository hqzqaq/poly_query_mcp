"""
配置管理模块
"""

import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseModel):
    """数据库配置基类"""
    host: str = Field(..., description="数据库主机地址")
    port: int = Field(..., description="数据库端口")
    username: Optional[str] = Field(None, description="用户名")
    password: Optional[str] = Field(None, description="密码")
    database: Optional[str] = Field(None, description="数据库名")
    
    class Config:
        extra = "allow"


class MySQLConfig(DatabaseConfig):
    """MySQL数据库配置"""
    port: int = Field(3306, description="MySQL默认端口")
    charset: str = Field("utf8mb4", description="字符集")


class PostgreSQLConfig(DatabaseConfig):
    """PostgreSQL数据库配置"""
    port: int = Field(5432, description="PostgreSQL默认端口")
    schema: Optional[str] = Field("public", description="PostgreSQL schema名称，默认为public")


class RedisConfig(DatabaseConfig):
    """Redis数据库配置"""
    port: int = Field(6379, description="Redis默认端口")
    db: int = Field(0, description="Redis数据库索引")


class MongoDBConfig(DatabaseConfig):
    """MongoDB数据库配置"""
    port: int = Field(27017, description="MongoDB默认端口")


class AppConfig(BaseSettings):
    """应用配置"""
    mysql: Optional[MySQLConfig] = None
    postgresql: Optional[PostgreSQLConfig] = None
    redis: Optional[RedisConfig] = None
    mongodb: Optional[MongoDBConfig] = None
    
    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
        case_sensitive = False
        
    @classmethod
    def load_from_dict(cls, config_dict: Dict[str, Any]) -> "AppConfig":
        """从字典加载配置"""
        mysql_config = None
        if "mysql" in config_dict:
            mysql_config = MySQLConfig(**config_dict["mysql"])
            
        postgresql_config = None
        if "postgresql" in config_dict:
            postgresql_config = PostgreSQLConfig(**config_dict["postgresql"])
            
        redis_config = None
        if "redis" in config_dict:
            redis_config = RedisConfig(**config_dict["redis"])
            
        mongodb_config = None
        if "mongodb" in config_dict:
            mongodb_config = MongoDBConfig(**config_dict["mongodb"])
            
        return cls(
            mysql=mysql_config,
            postgresql=postgresql_config,
            redis=redis_config,
            mongodb=mongodb_config
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {}
        if self.mysql:
            result["mysql"] = self.mysql.dict()
        if self.postgresql:
            result["postgresql"] = self.postgresql.dict()
        if self.redis:
            result["redis"] = self.redis.dict()
        if self.mongodb:
            result["mongodb"] = self.mongodb.dict()
        return result