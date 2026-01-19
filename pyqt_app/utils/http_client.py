"""HTTP 客户端工具"""
import requests
from typing import Dict, Optional
from utils.logger import get_logger

logger = get_logger()

class HttpClient:
    """统一的 HTTP 客户端"""
    
    def __init__(self):
        self.session = requests.Session()
        self.timeout = 10
    
    def get(self, url: str, headers: Optional[Dict] = None, params: Optional[Dict] = None) -> Optional[Dict]:
        """GET 请求"""
        try:
            response = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"GET 请求失败 {url}: {e}")
            return None
    
    def post(self, url: str, headers: Optional[Dict] = None, data: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Optional[Dict]:
        """POST 请求"""
        try:
            response = self.session.post(url, headers=headers, data=data, json=json_data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"POST 请求失败 {url}: {e}")
            return None
    
    def get_raw_response(self, url: str, headers: Optional[Dict] = None, json_data: Optional[Dict] = None):
        """获取原始响应（用于获取 headers）"""
        try:
            response = self.session.post(url, headers=headers, json=json_data, timeout=self.timeout)
            return response
        except requests.RequestException as e:
            logger.error(f"请求失败 {url}: {e}")
            return None

# 全局单例
_http_client = None

def get_http_client() -> HttpClient:
    """获取 HTTP 客户端实例"""
    global _http_client
    if _http_client is None:
        _http_client = HttpClient()
    return _http_client
