"""数据存储模块 - 使用 JSON 文件"""
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from utils.logger import get_logger

logger = get_logger()

class Storage:
    """统一的数据存储管理"""
    
    def __init__(self):
        # 数据保存在程序所在目录的 data 文件夹
        app_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.data_dir = app_dir / 'data'
        self.data_dir.mkdir(exist_ok=True)
        
        self.config_file = self.data_dir / 'config.json'
        self.tasks_file = self.data_dir / 'tasks.json'
        self.wishlist_file = self.data_dir / 'wishlist.json'
        
        self._ensure_files()
    
    def _ensure_files(self):
        """确保所有必要的文件存在"""
        if not self.config_file.exists():
            self._save_json(self.config_file, {
                'cookies': {},
                'device_id': ''
            })
        
        if not self.tasks_file.exists():
            self._save_json(self.tasks_file, [])
        
        if not self.wishlist_file.exists():
            self._save_json(self.wishlist_file, [])
    
    def _load_json(self, file_path: Path) -> Any:
        """加载 JSON 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载文件失败 {file_path}: {e}")
            return None
    
    def _save_json(self, file_path: Path, data: Any):
        """保存 JSON 文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"保存文件失败 {file_path}: {e}")
    
    # Config 相关
    def get_config(self) -> Dict:
        """获取配置"""
        return self._load_json(self.config_file) or {}
    
    def save_config(self, config: Dict):
        """保存配置"""
        self._save_json(self.config_file, config)
    
    def get_cookies(self) -> Dict:
        """获取 cookies"""
        config = self.get_config()
        return config.get('cookies', {})
    
    def save_cookies(self, cookies: Dict, device_id: str):
        """保存 cookies"""
        config = self.get_config()
        config['cookies'] = cookies
        config['device_id'] = device_id
        self.save_config(config)
    
    def get_device_id(self) -> str:
        """获取设备 ID"""
        config = self.get_config()
        return config.get('device_id', '')
    
    # Tasks 相关
    def get_tasks(self) -> List[Dict]:
        """获取任务列表"""
        return self._load_json(self.tasks_file) or []
    
    def save_tasks(self, tasks: List[Dict]):
        """保存任务列表"""
        self._save_json(self.tasks_file, tasks)
    
    def add_task(self, task: Dict):
        """添加任务"""
        tasks = self.get_tasks()
        tasks.append(task)
        self.save_tasks(tasks)
    
    def remove_task(self, task_name: str):
        """删除任务"""
        tasks = self.get_tasks()
        tasks = [t for t in tasks if t.get('name') != task_name]
        self.save_tasks(tasks)
    
    def clear_tasks(self):
        """清空任务列表"""
        self.save_tasks([])
    
    # Wishlist 相关
    def get_wishlist(self) -> List[Dict]:
        """获取心愿单"""
        return self._load_json(self.wishlist_file) or []
    
    def save_wishlist(self, wishlist: List[Dict]):
        """保存心愿单"""
        self._save_json(self.wishlist_file, wishlist)
    
    def add_to_wishlist(self, item: Dict):
        """添加到心愿单"""
        wishlist = self.get_wishlist()
        wishlist.append(item)
        self.save_wishlist(wishlist)
    
    def clear_wishlist(self):
        """清空心愿单"""
        self.save_wishlist([])

# 全局单例
_storage = None

def get_storage() -> Storage:
    """获取存储实例"""
    global _storage
    if _storage is None:
        _storage = Storage()
    return _storage
