import requests
from typing import Optional, List, Dict
import datetime
from .log import log_message



def getaddress(cookie):
    """
    获取地址
    """
    url = "https://api-takumi.mihoyogift.com/account/address/list"
    headers = {
        "Host": "api-takumi.mihoyogift.com",
        "Accept": "*/*",
        "Sec-Fetch-Site": "same-site",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        "Sec-Fetch-Mode": "cors",
        "Content-Type": "application/json",
        "Origin": "https://user.mihoyogift.com",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.72.1",
        "Referer": "https://user.mihoyogift.com/",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "Sec-Fetch-Dest": "empty"
    }

    res = requests.get(url, headers=headers)
    #print(res.text)
    return res.json()


#参考https://github.com/GOOD-AN/Mys-Exchange-Goods 感谢开源

def parse_goods_info(data: Dict) -> Dict:
    """
    解析商品信息
    """
    # 在这里实现实际的解析逻辑
    return data

def get_goods_biz() -> Optional[List[List[str]]]:
    """
    获取商品分区列表
    """
    goods_biz_url = "https://api-takumi.mihoyogift.com/mall/v1/web/goods/list"
    goods_biz_params = {
        "app_id": 1,
        "point_sn": "myb",
        "page_size": 20,
        "page": 1,
        "game": '',
    }

    try:
        res = requests.get(goods_biz_url, params=goods_biz_params)
        res.raise_for_status()  # 检查HTTP请求状态
        goods_biz_data = res.json()['data']
        goods_biz_map = map(lambda x: [x['name'], x['key']], goods_biz_data['games'])
        return [item for item in goods_biz_map if item[1] != 'all']  # 过滤掉key为'all'的项目
    except:
        return None

from datetime import datetime

def timestamp_to_date(timestamp, format='%Y-%m-%d %H:%M:%S'):
    """
    将时间戳转换为日期字符串，默认格式为 '%Y-%m-%d %H:%M:%S'
    """
    if timestamp is None:
        return None
    try:
        dt = datetime.fromtimestamp(int(str(timestamp)))
        return dt.strftime(format)
    except (ValueError, TypeError):
        return None

def parse_goods_info(goods):
    """
    解析商品信息，这里你可以根据实际需要解析具体的字段。
    """

    return {
        "id": goods.get("goods_id"),
        "name": goods.get("goods_name"),
        "price": goods.get("price"),
        "time": timestamp_to_date(goods.get("next_time")),
        "icon": goods.get("icon"),
    }

def get_goods_list(game_type: str, cookie: str = ''):
    """
    获取商品列表
    """
    goods_list_url = "https://api-takumi.mihoyogift.com/mall/v1/web/goods/list"
    goods_list_params = {
        "app_id": 1,
        "point_sn": "myb",
        "page_size": 20,
        "page": 1,
        "game": game_type,
    }
    goods_list_headers = {
        "Cookie": cookie,
    }

    goods_list = []

    try:
        while True:
            res = requests.get(goods_list_url, params=goods_list_params, headers=goods_list_headers)
            res.raise_for_status()  # 检查HTTP请求状态
            goods_list_data = res.json()['data']
            #print(goods_list_data)

            goods_list += list(map(parse_goods_info, goods_list_data['list']))
            # 判断是否需要获取下一页数据
            if goods_list_data['total'] > goods_list_params['page_size'] * goods_list_params['page']:
                goods_list_params['page'] += 1
            else:
                break
        return goods_list
    except:
        return None

def get_point(cookie):
    """
    获取米游币数量
    需要stoken与stuid
    """
        
    point_url = "https://bbs-api.mihoyo.com/apihub/sapi/getUserMissionsState"
    point_headers = {
        'Cookie': cookie,
    }
        
    point_req = requests.get(point_url, headers=point_headers)
        
    if point_req.status_code != 200:
        log_message(f"获取米游币数量失败, 返回状态码为{str(point_req.status_code)}")
        return False
        
    point_req = point_req.json()
        
    if point_req['retcode'] != 0:
        log_message(f"获取米游币数量失败, 原因为{point_req['message']}")
        return False
        
    return point_req['data']['total_points']





