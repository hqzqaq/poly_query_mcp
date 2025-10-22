"""
配置管理器
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

from .config import AppConfig

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or os.path.join(os.path.dirname(__file__), "config.json")
        self.config = None
        self.load_config()
    
    def load_config(self) -> None:
        """加载配置文件"""
        try:
            # 首先加载环境变量
            load_dotenv()
            
            # 检查配置文件是否存在
            if not os.path.exists(self.config_file):
                logger.warning(f"配置文件不存在: {self.config_file}，使用默认配置")
                self.config = self._get_default_config()
                self.save_config()  # 保存默认配置
                return
            
            # 加载配置文件
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 使用AppConfig加载配置
            self.config = AppConfig.load_from_dict(config_data)
            logger.info(f"成功加载配置文件: {self.config_file}")
        
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            logger.info("使用默认配置")
            self.config = self._get_default_config()
    
    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # 将配置转换为字典
            config_dict = self.config.to_dict()
            
            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置已保存到: {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")
            return False
    
    def get_config(self) -> AppConfig:
        """获取配置对象"""
        return self.config
    
    def update_config(self, config_data: Dict[str, Any]) -> bool:
        """更新配置"""
        try:
            # 创建新的配置对象
            new_config = AppConfig.load_from_dict(config_data)
            
            # 更新当前配置
            self.config = new_config
            
            # 保存配置
            return self.save_config()
        except Exception as e:
            logger.error(f"更新配置失败: {str(e)}")
            return False
    
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
                "database": os.getenv("POSTGRESQL_DATABASE", "")
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
    
    def create_sample_config(self, file_path: str) -> bool:
        """创建示例配置文件"""
        try:
            sample_config = {
                "mysql": {
                    "host": "localhost",
                    "port": 3306,
                    "user": "root",
                    "password": "your_password",
                    "database": "your_database"
                },
                "postgresql": {
                    "host": "localhost",
                    "port": 5432,
                    "user": "postgres",
                    "password": "your_password",
                    "database": "your_database"
                },
                "redis": {
                    "host": "localhost",
                    "port": 6379,
                    "db": 0,
                    "password": "your_password"
                },
                "mongodb": {
                    "host": "localhost",
                    "port": 27017,
                    "username": "your_username",
                    "password": "your_password",
                    "database": "your_database"
                }
            }
            
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 保存示例配置
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(sample_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"示例配置已创建: {file_path}")
            return True
        except Exception as e:
            logger.error(f"创建示例配置文件失败: {str(e)}")
            return False