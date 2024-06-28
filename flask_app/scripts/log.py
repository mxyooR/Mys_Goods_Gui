import logging
import os

# 定义基本目录和父目录路径
base_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.dirname(base_dir)
log_path = os.path.join(parent_dir, 'log.log')

def setup_logger(log_file=log_path):
    """设置自定义日志记录器"""
    logger = logging.getLogger('custom_logger')
    logger.setLevel(logging.INFO)

    # 检查日志记录器是否已经有处理程序，避免重复记录
    if not any(isinstance(handler, logging.FileHandler) for handler in logger.handlers):
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        # 文件处理程序，使用 UTF-8 编码写入文件
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 控制台处理程序
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        print(f"日志记录器已设置，日志文件: {log_file}")

def log_message(message):
    """记录日志信息"""
    logger = logging.getLogger('custom_logger')
    logger.info(message)
    print(f"已记录信息: {message}")
