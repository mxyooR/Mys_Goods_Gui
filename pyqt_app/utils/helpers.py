"""辅助工具函数"""
import random
from string import hexdigits
from typing import Dict

def generate_random_fp() -> str:
    """生成随机设备指纹"""
    prefix = "38d7"
    suffix = ''.join(random.choices(hexdigits.lower()[:16], k=9))
    return prefix + suffix

def get_region_by_game_biz(game_biz: str) -> str:
    """根据游戏类型获取区服"""
    region_map = {
        "hk4e": "cn_gf01",      # 原神
        "bh3": "android01",      # 崩坏3
        "hkrpg": "prod_gf_cn",   # 崩坏：星穹铁道
        "nap_cn": "prod_gf_cn",  # 绝区零
    }
    return region_map.get(game_biz, "")

def build_exchange_headers(cookie: str, device_id: str) -> Dict:
    """构建兑换请求头"""
    return {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 12; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36',
        'Accept': "application/json, text/plain, */*",
        'x-rpc-device_model': "MI 6",
        'Referer': "https://webstatic.miyoushe.com/",
        'x-rpc-device_name': "Xiaomi MI 6",
        'Origin': "https://webstatic.miyoushe.com",
        'x-rpc-device_fp': str(generate_random_fp()),
        'x-rpc-channel': "xiaomi",
        'Accept-Language': "zh-CN,zh-Hans;q=0.9",
        'x-rpc-app_version': "2.71.1",
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
    region = get_region_by_game_biz(game_biz)
    
    payload = {
        "app_id": 1,
        "point_sn": "myb",
        "goods_id": goods_id,
        "exchange_num": 1,
        "uid": uid,
        "region": region,
        "game_biz": game_biz,
    }
    
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
