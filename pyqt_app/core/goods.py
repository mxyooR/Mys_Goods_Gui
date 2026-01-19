"""商品相关服务"""
from typing import List, Dict, Optional
from datetime import datetime
from utils.http_client import get_http_client
from utils.logger import get_logger

logger = get_logger()

class GoodsService:
    """商品服务"""
    
    def __init__(self):
        self.http_client = get_http_client()
    
    def get_game_list(self) -> Optional[List[Dict]]:
        """获取游戏分区列表"""
        url = "https://api-takumi.mihoyogift.com/mall/v1/web/goods/list"
        params = {
            "app_id": 1,
            "point_sn": "myb",
            "page_size": 20,
            "page": 1,
            "game": '',
        }
        
        response = self.http_client.get(url, params=params)
        if not response or response.get('retcode') != 0:
            logger.error("获取游戏列表失败")
            return None
        
        games = response.get('data', {}).get('games', [])
        return [
            {'name': game['name'], 'key': game['key']}
            for game in games if game['key'] != 'all'
        ]
    
    def get_goods_list(self, game_type: str, cookie: str = '') -> Optional[List[Dict]]:
        """获取商品列表"""
        url = "https://api-takumi.mihoyogift.com/mall/v1/web/goods/list"
        headers = {"Cookie": cookie} if cookie else {}
        
        goods_list = []
        page = 1
        
        while True:
            params = {
                "app_id": 1,
                "point_sn": "myb",
                "page_size": 20,
                "page": page,
                "game": game_type,
            }
            
            response = self.http_client.get(url, params=params, headers=headers)
            if not response or response.get('retcode') != 0:
                logger.error(f"获取商品列表失败: {response}")
                break
            
            data = response.get('data', {})
            goods_list.extend([self._parse_goods(g) for g in data.get('list', [])])
            
            # 检查是否还有下一页
            if data.get('total', 0) > page * 20:
                page += 1
            else:
                break
        
        logger.info(f"获取到 {len(goods_list)} 个商品")
        return goods_list
    
    def _parse_goods(self, goods: Dict) -> Dict:
        """解析商品信息"""
        return {
            "id": goods.get("goods_id"),
            "name": goods.get("goods_name"),
            "price": goods.get("price"),
            "time": self._timestamp_to_date(goods.get("next_time")),
            "icon": goods.get("icon"),
            "type": goods.get("type"),
        }
    
    def _timestamp_to_date(self, timestamp, format='%Y-%m-%d %H:%M:%S') -> Optional[str]:
        """时间戳转日期字符串"""
        if timestamp is None:
            return None
        try:
            dt = datetime.fromtimestamp(int(str(timestamp)))
            return dt.strftime(format)
        except (ValueError, TypeError):
            return None
    
    def get_user_points(self, cookie: str) -> Optional[int]:
        """获取用户米游币数量"""
        url = "https://api-takumi.miyoushe.com/common/homutreasure/v1/web/user/point"
        params = {"app_id": 1, "point_sn": "myb"}
        headers = {"Cookie": cookie}
        
        response = self.http_client.get(url, params=params, headers=headers)
        if not response or response.get('retcode') != 0:
            logger.error("获取米游币数量失败")
            return None
        
        points = response.get('data', {}).get('points', 0)
        logger.info(f"当前米游币: {points}")
        return int(points)
    
    def get_address_list(self, cookie: str) -> Optional[List[Dict]]:
        """获取收货地址列表"""
        url = "https://api-takumi.mihoyogift.com/account/address/list"
        headers = {
            "Host": "api-takumi.mihoyogift.com",
            "Accept": "*/*",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.72.1",
            "Cookie": cookie,
        }
        
        response = self.http_client.get(url, headers=headers)
        if not response or response.get('retcode') != 0:
            logger.error("获取地址列表失败")
            return []
        
        addresses = response.get('data', {}).get('list', [])
        # 添加空地址选项（用于游戏内商品）
        addresses.append({'id': '', 'addr_ext': '空地址（游戏内商品）'})
        return addresses
