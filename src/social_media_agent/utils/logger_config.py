"""
日志系统配置
提供统一的日志配置和管理
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional
from datetime import datetime

from social_media_agent.config import LogConfig, PathConfig, DevConfig


class ColoredFormatter(logging.Formatter):
    """带颜色的控制台日志格式化器"""
    
    # ANSI 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
    }
    RESET = '\033[0m'
    
    # Emoji 图标
    ICONS = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️ ',
        'WARNING': '⚠️ ',
        'ERROR': '❌',
        'CRITICAL': '🔥',
    }
    
    def format(self, record):
        # 获取颜色
        levelname = record.levelname
        color = self.COLORS.get(levelname, self.RESET)
        icon = self.ICONS.get(levelname, '')
        
        # 添加颜色和图标
        record.levelname = f"{color}{icon} {levelname}{self.RESET}"
        record.name = f"{color}{record.name}{self.RESET}"
        
        return super().format(record)


class LoggerManager:
    """日志管理器"""
    
    _initialized = False
    _loggers = {}
    
    @classmethod
    def setup_logging(
        cls,
        level: Optional[str] = None,
        log_file: Optional[Path] = None,
        console_enabled: bool = True,
        file_enabled: bool = True,
        colorize: bool = True
    ):
        """
        配置全局日志系统
        
        Args:
            level: 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）
            log_file: 日志文件路径
            console_enabled: 是否启用控制台输出
            file_enabled: 是否启用文件输出
            colorize: 控制台是否使用颜色
        """
        if cls._initialized:
            return
        
        # 使用配置或参数
        log_level = level or LogConfig.LOG_LEVEL
        log_file = log_file or (LogConfig.LOGS_DIR / "agent.log")
        console_enabled = console_enabled if console_enabled is not None else LogConfig.LOG_CONSOLE_ENABLED
        file_enabled = file_enabled if file_enabled is not None else LogConfig.LOG_FILE_ENABLED
        colorize = colorize if colorize is not None else LogConfig.LOG_CONSOLE_COLORIZE
        
        # 确保日志目录存在
        if file_enabled and log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 获取根 Logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # 清除现有的 handlers
        root_logger.handlers.clear()
        
        # 控制台 Handler
        if console_enabled:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, log_level.upper()))
            
            if colorize and sys.stdout.isatty():
                # 使用带颜色的格式化器
                console_formatter = ColoredFormatter(
                    fmt='%(levelname)s %(name)s - %(message)s',
                    datefmt=LogConfig.LOG_DATE_FORMAT
                )
            else:
                # 普通格式化器
                console_formatter = logging.Formatter(
                    fmt='%(levelname)s %(name)s - %(message)s',
                    datefmt=LogConfig.LOG_DATE_FORMAT
                )
            
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
        
        # 文件 Handler
        if file_enabled and log_file:
            file_handler = RotatingFileHandler(
                filename=str(log_file),
                maxBytes=LogConfig.LOG_FILE_MAX_BYTES,
                backupCount=LogConfig.LOG_FILE_BACKUP_COUNT,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, log_level.upper()))
            
            # 文件日志使用详细格式
            file_formatter = logging.Formatter(
                fmt=LogConfig.LOG_FORMAT,
                datefmt=LogConfig.LOG_DATE_FORMAT
            )
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
        
        cls._initialized = True
        
        # 记录日志系统初始化信息
        logger = logging.getLogger('LoggerManager')
        logger.info("日志系统已初始化")
        logger.info(f"日志级别: {log_level}")
        logger.info(f"控制台输出: {'启用' if console_enabled else '禁用'}")
        logger.info(f"文件输出: {'启用' if file_enabled else '禁用'}")
        if file_enabled and log_file:
            logger.info(f"日志文件: {log_file}")
        if DevConfig.DEBUG:
            logger.debug("调试模式已启用")
        if DevConfig.MOCK_MODE:
            logger.info("🎭 Mock 模式已启用")
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        获取指定名称的 Logger
        
        Args:
            name: Logger 名称
            
        Returns:
            Logger 实例
        """
        if not cls._initialized:
            cls.setup_logging()
        
        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(name)
        
        return cls._loggers[name]
    
    @classmethod
    def set_level(cls, level: str):
        """
        动态设置日志级别
        
        Args:
            level: 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）
        """
        log_level = getattr(logging, level.upper())
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        for handler in root_logger.handlers:
            handler.setLevel(log_level)
        
        logger = cls.get_logger('LoggerManager')
        logger.info(f"日志级别已更改为: {level}")
    
    @classmethod
    def add_context(cls, **context):
        """
        添加上下文信息到所有日志
        
        Args:
            **context: 上下文键值对
        """
        # 可以通过 Filter 实现，这里提供一个简单的实现
        pass


def setup_logging(
    level: Optional[str] = None,
    console_enabled: bool = True,
    file_enabled: bool = True,
    colorize: bool = True
):
    """
    快捷函数：配置日志系统
    
    Args:
        level: 日志级别
        console_enabled: 是否启用控制台输出
        file_enabled: 是否启用文件输出
        colorize: 控制台是否使用颜色
    """
    LoggerManager.setup_logging(
        level=level,
        console_enabled=console_enabled,
        file_enabled=file_enabled,
        colorize=colorize
    )


def get_logger(name: str) -> logging.Logger:
    """
    快捷函数：获取 Logger
    
    Args:
        name: Logger 名称
        
    Returns:
        Logger 实例
    """
    return LoggerManager.get_logger(name)


# 日志装饰器
def log_execution(logger: Optional[logging.Logger] = None):
    """
    装饰器：记录函数执行
    
    Args:
        logger: Logger 实例（如果不提供则使用函数所在模块的 Logger）
    """
    import functools
    import time
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_logger(func.__module__)
            
            func_name = func.__name__
            logger.debug(f"开始执行: {func_name}")
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.debug(f"执行完成: {func_name} (耗时: {elapsed:.2f}秒)")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"执行失败: {func_name} (耗时: {elapsed:.2f}秒): {str(e)}")
                raise
        
        return wrapper
    return decorator


__all__ = [
    'LoggerManager',
    'setup_logging',
    'get_logger',
    'log_execution',
    'ColoredFormatter'
]

