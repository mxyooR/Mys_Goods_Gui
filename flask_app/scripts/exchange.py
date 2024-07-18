import httpx
import asyncio
import json
from datetime import datetime, timedelta
import ntplib
from concurrent.futures import ThreadPoolExecutor
from .log import log_message
import os
import global_vars


task_messages = []
base_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.dirname(base_dir)
goodslist_path = os.path.join(parent_dir, 'goodslist.json')
config_path = os.path.join(parent_dir, 'config.json')
tasklistpath = os.path.join(parent_dir, 'tasklist.json')

executor = ThreadPoolExecutor()

async def get_ntp_time():
    """
    获取NTP时间
    """
    client = ntplib.NTPClient()
    
    def fetch_ntp_time():
        try:
            response = client.request('ntp.aliyun.com')

            # 时区转换
            return datetime.utcfromtimestamp(response.tx_time) + timedelta(hours=8)
        except Exception as e:
            print(f"获取NTP时间失败: {e}")
            return None
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, fetch_ntp_time)


async def exchange_goods(payload, headers):
    """
    兑换商品
    """
    url = "https://api-takumi.miyoushe.com/mall/v1/web/goods/exchange"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, data=json.dumps(payload), headers=headers)
            task_messages.append(response.text)
            log_message(response.text)
            print(response.text)
        except httpx.HTTPStatusError as e:
            task_messages.append(f"HTTP error occurred: {e}")
            log_message(f"HTTP error occurred: {e}")
            print(f"HTTP error occurred: {e}")
        except Exception as e:
            task_messages.append(f"An error occurred: {e}")
            log_message(f"An error occurred: {e}")
            print(f"An error occurred: {e}")

async def schedule_task(task):
        payload = task["payload"]
        headers = task["headers"]
        target_time = datetime.fromisoformat(task["time"])
        

        while global_vars.task_running:
            
            ntp_time = await get_ntp_time()
            
            if ntp_time:

                ntp_time = ntp_time
                task_messages.append(f"现在是北京时间： {ntp_time}")
                print(f"在是北京时间： {ntp_time}")
                delay = (target_time - ntp_time).total_seconds()
                if delay <= 15:
                    await asyncio.sleep(delay)
                    await asyncio.gather(
                        exchange_goods(payload, headers),
                        exchange_goods(payload, headers),
                        exchange_goods(payload, headers),
                        exchange_goods(payload, headers),
                        exchange_goods(payload, headers)
                    )
                    break
                else:
                    
                    task_messages.append(f"目前还剩余 {delay} 秒. 10秒后重新校准时间")
                    await asyncio.sleep(10)
            else:
                task_messages.append("获取NTP时间失败. 1秒后重试")
                await asyncio.sleep(1)
