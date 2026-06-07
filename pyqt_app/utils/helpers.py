"""辅助工具函数"""
import random
from string import hexdigits
from typing import Dict

try:
    from utils.ext_utils import get_f as _x
except:
    _x = None

APP_VERSION = "2.108.0"

def generate_random_fp() -> str:
    """生成随机设备指纹"""
    prefix = "38d7"
    suffix = ''.join(random.choices(hexdigits.lower()[:16], k=9))
    return prefix + suffix if not _x else (_x(prefix) if callable(_x) else prefix + suffix)

def get_region_by_game_biz(game_biz: str) -> str:
    """根据游戏类型获取区服"""
    region_map = {
        "hk4e": "cn_gf01",       # 原神
        "hk4e_cn": "cn_gf01",
        "bh3": "android01",      # 崩坏3
        "bh3_cn": "android01",
        "hkrpg": "prod_gf_cn",   # 崩坏：星穹铁道
        "hkrpg_cn": "prod_gf_cn",
        "nap": "prod_gf_cn",     # 绝区零
        "nap_cn": "prod_gf_cn",
    }
    return region_map.get(game_biz, "")

def normalize_game_biz(game_biz: str) -> str:
    """将商品列表的游戏 key 转成兑换接口需要的 game_biz。"""
    game_biz_map = {
        "hk4e": "hk4e_cn",
        "bh3": "bh3_cn",
        "hkrpg": "hkrpg_cn",
        "nap": "nap_cn",
        "bbs": "bbs",
    }
    return game_biz_map.get(game_biz, game_biz)

def build_exchange_headers(cookie: str, device_id: str) -> Dict:
    """构建兑换请求头"""
    return {
        'User-Agent': f'Mozilla/5.0 (Linux; Android 12; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36 miHoYoBBS/{APP_VERSION}',
        'Accept': "application/json, text/plain, */*",
        'x-rpc-device_model': "MI 6",
        'Referer': "https://webstatic.miyoushe.com/",
        'x-rpc-device_name': "Xiaomi MI 6",
        'Origin': "https://webstatic.miyoushe.com",
        'Sec-Fetch-Dest': "empty",
        'Sec-Fetch-Site': "same-site",
        'Sec-Fetch-Mode': "cors",
        'x-rpc-device_fp': str(generate_random_fp() if not _x else (_x(device_id) if callable(_x) else generate_random_fp())),
        'x-rpc-channel': "xiaomi",
        'Accept-Language': "zh-CN,zh-Hans;q=0.9",
        'x-rpc-app_version': APP_VERSION,
        'x-rpc-client_type': "1",
        'x-rpc-verify_key': "bll8iq97cem8",
        'x-rpc-device_id': device_id,
        'Content-Type': "application/json; charset=utf-8",
        'x-rpc-sys_version': "12",
        'Cookie': cookie
    }

def build_task_config(
    name: str,
    goods_id: str,
    uid: str,
    game_biz: str,
    address_id: str,
    device_id: str,
    cookie: str,
    time: str,
    count: int = 5
) -> Dict:
    """构建任务配置"""
    normalized_game_biz = normalize_game_biz(game_biz)
    region = get_region_by_game_biz(normalized_game_biz)
    
    payload = {
        "app_id": 1,
        "point_sn": "myb",
        "goods_id": goods_id,
        "exchange_num": 1,
        "uid": uid,
        "game_biz": normalized_game_biz,
    }

    if region:
        payload["region"] = region
    
    if address_id:
        payload["address_id"] = address_id
    
    headers = build_exchange_headers(cookie, device_id)
    
    return {
        "name": name,
        "payload": payload,
        "headers": headers,
        "time": time,
        "count": count
    }
