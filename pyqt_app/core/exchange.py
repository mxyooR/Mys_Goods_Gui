"""兑换任务模块"""
import asyncio
import httpx
import json
import ntplib
from datetime import datetime, timedelta
from typing import Dict
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from utils.logger import get_logger
from utils.helpers import generate_random_fp

logger = get_logger()

class ExchangeTask(QObject):
    """兑换任务"""
    
    # 信号
    message_signal = pyqtSignal(str)  # 任务消息
    completed_signal = pyqtSignal(str)  # 任务完成
    error_signal = pyqtSignal(str, str)  # 任务名, 错误信息
    
    def __init__(self, task_config: Dict):
        super().__init__()
        self.name = task_config['name']
        self.payload = task_config['payload']
        self.headers = task_config['headers']
        self.target_time = datetime.fromisoformat(task_config['time'])
        self.count = task_config.get('count', 5)
        self.running = False
    
    async def get_ntp_time(self) -> datetime:
        """获取 NTP 时间"""
        try:
            client = ntplib.NTPClient()
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: client.request('ntp.aliyun.com', timeout=5)
            )
            # 转换为北京时间
            return datetime.utcfromtimestamp(response.tx_time) + timedelta(hours=8)
        except Exception as e:
            logger.error(f"获取 NTP 时间失败: {e}")
            return datetime.now()
    
    async def exchange_goods(self):
        """执行兑换"""
        url = "https://api-takumi.miyoushe.com/mall/v1/web/goods/exchange"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    data=json.dumps(self.payload),
                    headers=self.headers,
                    timeout=10
                )
                result = response.text
                self.message_signal.emit(f"[{self.name}] {result}")
                logger.info(f"任务 {self.name} 返回: {result}")
            except Exception as e:
                error_msg = f"兑换失败: {e}"
                self.message_signal.emit(f"[{self.name}] {error_msg}")
                logger.error(f"任务 {self.name} {error_msg}")
    
    async def run(self):
        """运行任务"""
        self.running = True
        logger.info(f"任务 {self.name} 已启动，目标时间: {self.target_time}")
        self.message_signal.emit(f"[{self.name}] 任务已启动，目标时间: {self.target_time}")
        
        while self.running:
            ntp_time = await self.get_ntp_time()
            delay = (self.target_time - ntp_time).total_seconds()
            
            if delay <= 60:
                # 距离目标时间不到60秒，等待并执行
                if delay > 0:
                    self.message_signal.emit(f"[{self.name}] 还剩 {delay:.1f} 秒，准备执行...")
                    await asyncio.sleep(delay)
                
                # 并发执行多次兑换
                tasks = [self.exchange_goods() for _ in range(self.count)]
                await asyncio.gather(*tasks)
                
                self.message_signal.emit(f"[{self.name}] 任务执行完成")
                logger.info(f"任务 {self.name} 执行完成")
                self.completed_signal.emit(self.name)
                self.running = False
                break
            else:
                # 距离目标时间较远，每30秒校准一次
                self.message_signal.emit(f"[{self.name}] 当前时间: {ntp_time.strftime('%H:%M:%S')}, 还剩 {delay:.0f} 秒")
                await asyncio.sleep(min(30, delay - 60))
    
    def stop(self):
        """停止任务"""
        self.running = False
        logger.info(f"任务 {self.name} 已停止")


class ExchangeWorker(QThread):
    """兑换任务工作线程"""
    
    def __init__(self, task: ExchangeTask):
        super().__init__()
        self.task = task
    
    def run(self):
        """运行任务"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.task.run())
        finally:
            loop.close()
    
    def stop(self):
        """停止任务"""
        self.task.stop()
        self.quit()
        self.wait()
