"""日志工具模块"""
import logging
import os
from pathlib import Path

def setup_logger(log_file='app.log'):
    """设置日志记录器"""
    # 日志保存在程序所在目录的 logs 文件夹
    app_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_dir = app_dir / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / log_file
    
    logger = logging.getLogger('mys_goods')
    logger.setLevel(logging.INFO)
    
    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器
    file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def get_logger():
    """获取日志记录器实例"""
    return logging.getLogger('mys_goods')
