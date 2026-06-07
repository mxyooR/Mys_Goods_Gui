"""认证模块 - 处理登录相关逻辑"""
import uuid
import re
import time
from http.cookies import SimpleCookie
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
    
    APP_VERSION = "2.108.0"
    DEVICE_NAME = "Xiaomi MI 6"
    DEVICE_MODEL = "MI 6"
    LATEST_COOKIE_NAMES = [
        "account_id_v2",
        "account_mid_v2",
        "cookie_token_v2",
        "ltmid_v2",
        "ltoken_v2",
        "ltuid_v2",
    ]
    COMPAT_COOKIE_NAMES = [
        "account_id",
        "cookie_token",
        "ltoken",
        "ltuid",
    ]
    
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
                        cookies = self._parse_cookies(
                            response.headers.get('Set-Cookie', ''),
                            response.cookies.get_dict(),
                        )
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
    
    def _parse_cookies(self, set_cookie: str, response_cookies: Optional[Dict] = None) -> Optional[Dict]:
        """解析 Cookie 字符串"""
        cookie_dict = dict(response_cookies or {})

        parsed = SimpleCookie()
        try:
            parsed.load(set_cookie)
            cookie_dict.update({name: morsel.value for name, morsel in parsed.items()})
        except Exception:
            for name, value in re.findall(r'([^=;\s]+)=([^;]+)', set_cookie):
                cookie_dict[name] = value

        cookie_dict = self._normalize_cookies(cookie_dict)
        return cookie_dict if self._has_supported_cookies(cookie_dict) else None
    
    def parse_manual_cookies(self, cookie_str: str) -> Optional[Dict]:
        """解析手动输入的 Cookie"""
        try:
            cookies = cookie_str.split('; ')
            cookie_dict = {}
            for cookie in cookies:
                if '=' in cookie:
                    key, value = cookie.split('=', 1)
                    cookie_dict[key] = value
            
            cookie_dict = self._normalize_cookies(cookie_dict)
            if self._has_supported_cookies(cookie_dict):
                return cookie_dict
            return None
        except Exception as e:
            logger.error(f"解析 Cookie 失败: {e}")
            return None

    @classmethod
    def _normalize_cookies(cls, cookies: Dict) -> Dict:
        """补齐新版 v2 Cookie 名，同时保留旧版兼容字段。"""
        normalized = {k.strip(): v.strip() for k, v in cookies.items() if k and v}

        account_id = normalized.get("account_id") or normalized.get("ltuid") or normalized.get("account_id_v2") or normalized.get("ltuid_v2")
        mid = normalized.get("account_mid_v2") or normalized.get("ltmid_v2")
        cookie_token = normalized.get("cookie_token") or normalized.get("cookie_token_v2")
        ltoken = normalized.get("ltoken") or normalized.get("ltoken_v2")

        if account_id:
            normalized.setdefault("account_id", account_id)
            normalized.setdefault("ltuid", account_id)
            normalized.setdefault("account_id_v2", account_id)
            normalized.setdefault("ltuid_v2", account_id)
        if mid:
            normalized.setdefault("account_mid_v2", mid)
            normalized.setdefault("ltmid_v2", mid)
        if cookie_token:
            normalized.setdefault("cookie_token", cookie_token)
            normalized.setdefault("cookie_token_v2", cookie_token)
        if ltoken:
            normalized.setdefault("ltoken", ltoken)
            normalized.setdefault("ltoken_v2", ltoken)

        return normalized

    @classmethod
    def _has_supported_cookies(cls, cookies: Dict) -> bool:
        """校验当前 Cookie 是否满足新版或兼容版登录态。"""
        latest_ok = all(name in cookies for name in cls.LATEST_COOKIE_NAMES)
        compat_ok = all(name in cookies for name in cls.COMPAT_COOKIE_NAMES) and "account_mid_v2" in cookies
        return latest_ok or compat_ok
    
    @staticmethod
    def cookies_to_string(cookies: Dict) -> str:
        """将 Cookie 字典转换为字符串"""
        normalized = AuthService._normalize_cookies(cookies)
        return ';'.join(f"{k}={v}" for k, v in normalized.items())
