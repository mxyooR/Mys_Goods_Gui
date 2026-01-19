"""认证模块 - 处理登录相关逻辑"""
import uuid
import re
import time
from typing import Tuple, Optional, Dict
from qrcode.main import QRCode
from PyQt6.QtCore import QObject, pyqtSignal
from utils.http_client import get_http_client
from utils.logger import get_logger

logger = get_logger()

class AuthService(QObject):
    """认证服务"""
    
    # 信号
    qr_generated = pyqtSignal(str, str)  # qr_url, ticket
    login_success = pyqtSignal(dict, str)  # cookies, device_id
    login_failed = pyqtSignal(str)  # error_message
    
    APP_VERSION = "2.71.1"
    DEVICE_NAME = "Xiaomi MI 6"
    DEVICE_MODEL = "MI 6"
    
    def __init__(self):
        super().__init__()
        self.http_client = get_http_client()
        self.device_id = uuid.uuid4().hex
        self._checking = False
    
    def _get_headers(self) -> Dict:
        """获取请求头"""
        return {
            "x-rpc-app_version": self.APP_VERSION,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-rpc-game_biz": "bbs_cn",
            "x-rpc-sys_version": "12",
            "x-rpc-device_id": self.device_id,
            "x-rpc-device_name": self.DEVICE_NAME,
            "x-rpc-device_model": self.DEVICE_MODEL,
            "x-rpc-app_id": "bll8iq97cem8",
            "x-rpc-client_type": "4",
            "User-Agent": "okhttp/4.9.3",
        }
    
    def generate_qr_code(self) -> Tuple[Optional[str], Optional[str]]:
        """生成二维码"""
        url = "https://passport-api.miyoushe.com/account/ma-cn-passport/web/createQRLogin"
        
        response = self.http_client.post(url, headers=self._get_headers())
        if not response or response.get('retcode') != 0:
            logger.error("生成二维码失败")
            return None, None
        
        data = response.get('data', {})
        qr_url = data.get('url')
        ticket = data.get('ticket')
        
        logger.info("二维码生成成功")
        self.qr_generated.emit(qr_url, ticket)
        return qr_url, ticket
    
    def create_qr_image(self, qr_url: str) -> QRCode:
        """创建二维码图片对象"""
        qr = QRCode()
        qr.add_data(qr_url)
        return qr.make_image(fill_color="black", back_color="white")
    
    def start_checking_login(self, ticket: str):
        """开始检查登录状态（在后台线程中调用）"""
        self._checking = True
        url = 'https://passport-api.miyoushe.com/account/ma-cn-passport/web/queryQRLoginStatus'
        data = {"ticket": ticket}
        
        while self._checking:
            response = self.http_client.get_raw_response(url, headers=self._get_headers(), json_data=data)
            
            if not response:
                time.sleep(2)
                continue
            
            try:
                res = response.json()
                
                if res.get('retcode') == 0:
                    status = res.get('data', {}).get('status')
                    
                    if status == "Created":
                        logger.info("等待扫码确认...")
                    elif status == "Confirmed":
                        logger.info("登录成功")
                        cookies = self._parse_cookies(response.headers.get('Set-Cookie', ''))
                        if cookies:
                            self.login_success.emit(cookies, self.device_id)
                        else:
                            self.login_failed.emit("解析 Cookie 失败")
                        self._checking = False
                        return
                else:
                    logger.error(f"检查登录状态失败: {res.get('message')}")
                    self.login_failed.emit(res.get('message', '未知错误'))
                    self._checking = False
                    return
            except Exception as e:
                logger.error(f"解析响应失败: {e}")
            
            time.sleep(2)
    
    def stop_checking(self):
        """停止检查登录状态"""
        self._checking = False
    
    def _parse_cookies(self, set_cookie: str) -> Optional[Dict]:
        """解析 Cookie 字符串"""
        cookie_dict = {}
        cookie_names = ['account_id', 'ltoken', 'ltuid', 'cookie_token', 'account_mid_v2']
        
        for name in cookie_names:
            match = re.search(rf'{name}=([^;]+)', set_cookie)
            if match:
                cookie_dict[name] = match.group(1)
        
        return cookie_dict if len(cookie_dict) == len(cookie_names) else None
    
    def parse_manual_cookies(self, cookie_str: str) -> Optional[Dict]:
        """解析手动输入的 Cookie"""
        try:
            cookies = cookie_str.split('; ')
            cookie_dict = {}
            for cookie in cookies:
                if '=' in cookie:
                    key, value = cookie.split('=', 1)
                    cookie_dict[key] = value
            
            # 验证必要的字段
            required = ['ltoken', 'ltuid', 'account_id', 'cookie_token', 'account_mid_v2']
            if all(key in cookie_dict for key in required):
                return {key: cookie_dict[key] for key in required}
            return None
        except Exception as e:
            logger.error(f"解析 Cookie 失败: {e}")
            return None
    
    @staticmethod
    def cookies_to_string(cookies: Dict) -> str:
        """将 Cookie 字典转换为字符串"""
        return ';'.join(f"{k}={v}" for k, v in cookies.items())
