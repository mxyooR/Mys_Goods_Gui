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
        self.time_offset = 0  # 本地时间与 NTP 时间的偏移（秒）
    
    async def get_ntp_time(self) -> datetime:
        """获取 NTP 时间"""
        try:
            client = ntplib.NTPClient()
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: client.request('ntp.aliyun.com', timeout=5)
            )
            # 转换为北京时间
            ntp_time = datetime.utcfromtimestamp(response.tx_time) + timedelta(hours=8)
            # 计算时间偏移
            local_time = datetime.now()
            self.time_offset = (ntp_time - local_time).total_seconds()
            logger.info(f"NTP 时间校准成功，偏移: {self.time_offset:.3f} 秒")
            return ntp_time
        except Exception as e:
            logger.error(f"获取 NTP 时间失败: {e}")
            return datetime.now()
    
    def get_corrected_time(self) -> datetime:
        """获取校正后的本地时间（使用缓存的偏移量）"""
        return datetime.now() + timedelta(seconds=self.time_offset)
    
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
        
        # 首次获取 NTP 时间并计算偏移
        await self.get_ntp_time()
        
        while self.running:
            # 使用校正后的本地时间，避免频繁请求 NTP
            current_time = self.get_corrected_time()
            delay = (self.target_time - current_time).total_seconds()
            
            if delay <= 5:
                # 距离目标时间不到 5 秒，进入精确等待模式
                if delay > 0:
                    self.message_signal.emit(f"[{self.name}] 还剩 {delay:.3f} 秒，准备执行...")
                    precise_delay = max(0, delay - 0.05)
                    await asyncio.sleep(precise_delay)
                
                # 并发执行多次兑换
                logger.info(f"任务 {self.name} 开始执行兑换，实际时间: {datetime.now()}")
                tasks = [self.exchange_goods() for _ in range(self.count)]
                await asyncio.gather(*tasks)
                
                self.message_signal.emit(f"[{self.name}] 任务执行完成")
                logger.info(f"任务 {self.name} 执行完成")
                self.completed_signal.emit(self.name)
                self.running = False
                break
            elif delay <= 60:
                # 距离目标时间 5-60 秒，每秒更新一次
                self.message_signal.emit(f"[{self.name}] 还剩 {delay:.1f} 秒")
                await asyncio.sleep(1)
            elif delay <= 300:
                # 距离目标时间 1-5 分钟，每 5 秒校准一次 NTP
                self.message_signal.emit(f"[{self.name}] 还剩 {delay:.0f} 秒")
                await self.get_ntp_time()  # 重新校准
                for _ in range(5):
                    if not self.running:
                        break
                    await asyncio.sleep(1)
            else:
                # 距离目标时间较远，每 30 秒校准一次 NTP
                self.message_signal.emit(f"[{self.name}] 当前时间: {current_time.strftime('%H:%M:%S')}, 还剩 {delay:.0f} 秒")
                await self.get_ntp_time()  # 重新校准
                sleep_time = min(30, delay - 60)
                for _ in range(int(sleep_time)):
                    if not self.running:
                        break
                    await asyncio.sleep(1)
    
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
        # 不要 wait()，让线程自己退出
        self.quit()
