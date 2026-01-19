"""任务管理界面"""
import os
import sys
import subprocess
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                             QDialog, QFormLayout, QLineEdit, QComboBox,
                             QSpinBox, QDateTimeEdit, QMessageBox, QTextEdit)
from PyQt6.QtCore import Qt, QDateTime
from core.goods import GoodsService
from core.exchange import ExchangeTask, ExchangeWorker
from core.auth import AuthService
from utils.storage import get_storage
from utils.helpers import build_task_config
from utils.logger import get_logger

logger = get_logger()

class CreateTaskDialog(QDialog):
    """创建任务对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.storage = get_storage()
        self.goods_service = GoodsService()
        self.init_ui()
    
    def init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("创建任务")
        self.setMinimumWidth(550)
        
        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # 任务名称
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入任务名称")
        layout.addRow("任务名称：", self.name_input)
        
        # 从心愿单选择商品
        self.goods_combo = QComboBox()
        self.goods_combo.currentIndexChanged.connect(self.on_goods_changed)
        layout.addRow("选择商品：", self.goods_combo)
        
        # 地址选择
        self.address_combo = QComboBox()
        layout.addRow("收货地址：", self.address_combo)
        
        # 兑换时间
        self.time_edit = QDateTimeEdit()
        self.time_edit.setDateTime(QDateTime.currentDateTime())
        self.time_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.time_edit.setCalendarPopup(True)
        layout.addRow("兑换时间：", self.time_edit)
        
        # 请求次数
        self.count_spin = QSpinBox()
        self.count_spin.setMinimum(1)
        self.count_spin.setMaximum(20)
        self.count_spin.setValue(5)
        layout.addRow("请求次数：", self.count_spin)
        
        # 加载数据 - 在所有控件创建完成后
        self.load_wishlist()
        self.load_addresses()
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        create_btn = QPushButton("创建")
        create_btn.clicked.connect(self.create_task)
        button_layout.addWidget(create_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("background-color: #6c757d;")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow("", button_layout)
    
    def load_wishlist(self):
        """加载心愿单"""
        wishlist = self.storage.get_wishlist()
        self.goods_combo.clear()
        
        if not wishlist:
            self.goods_combo.addItem("心愿单为空", None)
            return
        
        for item in wishlist:
            display_text = f"{item['name']} - {item['time']}"
            self.goods_combo.addItem(display_text, item)
        
        # 加载完成后触发一次时间更新
        if wishlist:
            self.on_goods_changed(0)
    
    def load_addresses(self):
        """加载地址列表"""
        cookies = self.storage.get_cookies()
        cookie_str = AuthService.cookies_to_string(cookies)
        
        addresses = self.goods_service.get_address_list(cookie_str)
        self.address_combo.clear()
        
        if addresses:
            for addr in addresses:
                display_text = addr.get('addr_ext', '未知地址')
                self.address_combo.addItem(display_text, addr.get('id', ''))
    
    def on_goods_changed(self, index):
        """商品切换事件"""
        goods = self.goods_combo.currentData()
        if goods and goods.get('time'):
            # 自动填充兑换时间
            try:
                dt = QDateTime.fromString(goods['time'], "yyyy-MM-dd HH:mm:ss")
                if dt.isValid():
                    self.time_edit.setDateTime(dt)
                    logger.info(f"自动填充时间: {goods['time']}")
            except Exception as e:
                logger.error(f"解析时间失败: {e}")
    
    def create_task(self):
        """创建任务"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请输入任务名称")
            return
        
        goods = self.goods_combo.currentData()
        if not goods:
            QMessageBox.warning(self, "提示", "请选择商品")
            return
        
        # 获取配置
        cookies = self.storage.get_cookies()
        cookie_str = AuthService.cookies_to_string(cookies)
        device_id = self.storage.get_device_id()
        uid = cookies.get('account_id', '')
        
        # 构建任务配置
        task_config = build_task_config(
            name=name,
            goods_id=goods['id'],
            uid=uid,
            game_biz=goods['biz'],
            address_id=self.address_combo.currentData() or '',
            device_id=device_id,
            cookie=cookie_str,
            time=self.time_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
            count=self.count_spin.value()
        )
        
        # 保存任务
        self.storage.add_task(task_config)
        logger.info(f"创建任务: {name}")
        
        self.accept()


class TaskWidget(QWidget):
    """任务管理界面"""
    
    def __init__(self):
        super().__init__()
        self.storage = get_storage()
        self.running_tasks = {}  # {task_name: ExchangeWorker}
        self.init_ui()
    
    def init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)
        
        # 顶部按钮
        top_layout = QHBoxLayout()
        
        create_btn = QPushButton("创建任务")
        create_btn.clicked.connect(self.create_task)
        top_layout.addWidget(create_btn)
        
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.load_tasks)
        top_layout.addWidget(refresh_btn)
        
        clear_btn = QPushButton("清空任务列表")
        clear_btn.clicked.connect(self.clear_tasks)
        top_layout.addWidget(clear_btn)
        
        open_file_btn = QPushButton("打开任务文件")
        open_file_btn.clicked.connect(self.open_task_file)
        top_layout.addWidget(open_file_btn)
        
        top_layout.addStretch()
        
        layout.addLayout(top_layout)
        
        # 任务表格
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(5)
        self.task_table.setHorizontalHeaderLabels([
            "任务名称", "兑换时间", "请求次数", "状态", "操作"
        ])
        
        header = self.task_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # 任务名称自适应
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # 时间固定
        self.task_table.setColumnWidth(1, 160)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # 次数固定
        self.task_table.setColumnWidth(2, 80)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # 状态固定
        self.task_table.setColumnWidth(3, 80)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # 操作固定
        self.task_table.setColumnWidth(4, 180)  # 足够容纳两个按钮
        
        # 设置行高 - 重要！
        self.task_table.verticalHeader().setDefaultSectionSize(80)
        self.task_table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.task_table)
        
        # 日志显示
        log_label = QLabel("任务日志:")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        layout.addWidget(self.log_text)
        
        # 加载任务
        self.load_tasks()
    
    def create_task(self):
        """创建任务"""
        dialog = CreateTaskDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_tasks()
            QMessageBox.information(self, "成功", "任务创建成功")
    
    def load_tasks(self):
        """加载任务列表"""
        tasks = self.storage.get_tasks()
        self.task_table.setRowCount(len(tasks))
        
        for row, task in enumerate(tasks):
            # 任务名称
            self.task_table.setItem(row, 0, QTableWidgetItem(task['name']))
            
            # 兑换时间
            self.task_table.setItem(row, 1, QTableWidgetItem(task['time']))
            
            # 请求次数
            self.task_table.setItem(row, 2, QTableWidgetItem(str(task.get('count', 5))))
            
            # 状态
            status = "运行中" if task['name'] in self.running_tasks else "未运行"
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.task_table.setItem(row, 3, status_item)
            
            # 操作按钮 - 直接放在单元格中
            if task['name'] in self.running_tasks:
                stop_btn = QPushButton("停止")
                stop_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #007bff;
                        color: #ffffff;
                        border: none;
                        padding: 6px 12px;
                        border-radius: 4px;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: #0069d9;
                    }
                """)
                stop_btn.clicked.connect(lambda checked, t=task: self.stop_task(t))
                self.task_table.setCellWidget(row, 4, stop_btn)
            else:
                # 创建容器来放置两个按钮
                button_container = QWidget()
                button_layout = QHBoxLayout(button_container)
                button_layout.setContentsMargins(2, 2, 2, 2)
                button_layout.setSpacing(5)
                
                start_btn = QPushButton("启动")
                start_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #007bff;
                        color: #ffffff;
                        border: none;
                        padding: 6px 12px;
                        border-radius: 4px;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: #0069d9;
                    }
                """)
                start_btn.clicked.connect(lambda checked, t=task: self.start_task(t))
                button_layout.addWidget(start_btn)
                
                delete_btn = QPushButton("删除")
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #dc3545;
                        color: #ffffff;
                        border: none;
                        padding: 6px 12px;
                        border-radius: 4px;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: #c82333;
                    }
                """)
                delete_btn.clicked.connect(lambda checked, t=task: self.delete_task(t))
                button_layout.addWidget(delete_btn)
                
                self.task_table.setCellWidget(row, 4, button_container)
    
    def start_task(self, task_config: dict):
        """启动任务"""
        task_name = task_config['name']
        
        if task_name in self.running_tasks:
            QMessageBox.warning(self, "提示", "任务已在运行中")
            return
        
        # 创建任务
        task = ExchangeTask(task_config)
        task.message_signal.connect(self.on_task_message)
        task.completed_signal.connect(self.on_task_completed)
        
        # 创建工作线程
        worker = ExchangeWorker(task)
        worker.start()
        
        self.running_tasks[task_name] = worker
        self.load_tasks()
        
        logger.info(f"启动任务: {task_name}")
        self.log_text.append(f"[{task_name}] 任务已启动")
    
    def stop_task(self, task_config: dict):
        """停止任务"""
        task_name = task_config['name']
        
        if task_name not in self.running_tasks:
            return
        
        worker = self.running_tasks[task_name]
        worker.stop()
        del self.running_tasks[task_name]
        
        self.load_tasks()
        logger.info(f"停止任务: {task_name}")
        self.log_text.append(f"[{task_name}] 任务已停止")
    
    def delete_task(self, task_config: dict):
        """删除任务"""
        reply = QMessageBox.question(
            self,
            "确认",
            f"确定要删除任务 '{task_config['name']}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.storage.remove_task(task_config['name'])
            self.load_tasks()
            logger.info(f"删除任务: {task_config['name']}")
    
    def clear_tasks(self):
        """清空任务列表"""
        if self.running_tasks:
            QMessageBox.warning(self, "提示", "请先停止所有运行中的任务")
            return
        
        reply = QMessageBox.question(
            self,
            "确认",
            "确定要清空任务列表吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.storage.clear_tasks()
            self.load_tasks()
            logger.info("任务列表已清空")
    
    def open_task_file(self):
        """打开任务列表文件"""
        task_file = self.storage.tasks_file
        
        if not task_file.exists():
            QMessageBox.information(self, "提示", "任务文件不存在")
            return
        
        try:
            # 跨平台打开文件
            if sys.platform == 'win32':
                os.startfile(task_file)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', task_file])
            else:  # Linux
                subprocess.run(['xdg-open', task_file])
        except Exception as e:
            QMessageBox.warning(self, "错误", f"打开文件失败: {e}")
    
    def on_task_message(self, message: str):
        """任务消息回调"""
        self.log_text.append(message)
        # 自动滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def on_task_completed(self, task_name: str):
        """任务完成回调"""
        if task_name in self.running_tasks:
            del self.running_tasks[task_name]
        self.load_tasks()
    
    def stop_all_tasks(self):
        """停止所有任务"""
        for worker in self.running_tasks.values():
            worker.stop()
        self.running_tasks.clear()
