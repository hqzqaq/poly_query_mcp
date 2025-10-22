"""
自定义异常类
"""

from typing import Optional, Any


class PolyQueryMCPError(Exception):
    """Poly Query MCP基础异常类"""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class DatabaseConnectionError(PolyQueryMCPError):
    """数据库连接错误"""
    pass


class DatabaseQueryError(PolyQueryMCPError):
    """数据库查询错误"""
    pass


class ConfigurationError(PolyQueryMCPError):
    """配置错误"""
    pass


class ValidationError(PolyQueryMCPError):
    """验证错误"""
    pass


class AuthenticationError(PolyQueryMCPError):
    """认证错误"""
    pass


class PermissionError(PolyQueryMCPError):
    """权限错误"""
    pass


class ResourceNotFoundError(PolyQueryMCPError):
    """资源未找到错误"""
    pass


class TimeoutError(PolyQueryMCPError):
    """超时错误"""
    pass


class RateLimitError(PolyQueryMCPError):
    """速率限制错误"""
    pass