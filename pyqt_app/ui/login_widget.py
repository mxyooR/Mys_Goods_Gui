"""登录界面"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QTextEdit, QTabWidget, QMessageBox)
from PyQt6.QtCore import pyqtSignal, QThread, Qt
from PyQt6.QtGui import QPixmap
from core.auth import AuthService
from utils.storage import get_storage
from utils.logger import get_logger
import uuid

logger = get_logger()

class LoginCheckThread(QThread):
    """登录检查线程"""
    
    def __init__(self, auth_service: AuthService, ticket: str):
        super().__init__()
        self.auth_service = auth_service
        self.ticket = ticket
    
    def run(self):
        self.auth_service.start_checking_login(self.ticket)

class LoginWidget(QWidget):
    """登录界面"""
    
    login_success = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.storage = get_storage()
        self.auth_service = AuthService()
        self.check_thread = None
        
        # 连接信号
        self.auth_service.login_success.connect(self.on_login_success)
        self.auth_service.login_failed.connect(self.on_login_failed)
        
        self.init_ui()
    
    def init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)
        
        # 标签页
        tabs = QTabWidget()
        
        # 二维码登录
        qr_widget = self.create_qr_login_widget()
        tabs.addTab(qr_widget, "扫码登录")
        
        # 手动登录
        manual_widget = self.create_manual_login_widget()
        tabs.addTab(manual_widget, "手动登录")
        
        layout.addWidget(tabs)
    
    def create_qr_login_widget(self) -> QWidget:
        """创建二维码登录界面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 说明
        info_label = QLabel("使用米游社 App 扫描二维码登录")
        info_label.setStyleSheet("font-size: 14px; padding: 10px;")
        layout.addWidget(info_label)
        
        # 二维码显示区域
        self.qr_label = QLabel()
        self.qr_label.setFixedSize(300, 300)
        self.qr_label.setStyleSheet("border: 1px solid #ccc; background-color: white;")
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.qr_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 生成二维码按钮
        self.generate_qr_btn = QPushButton("生成二维码")
        self.generate_qr_btn.clicked.connect(self.generate_qr_code)
        layout.addWidget(self.generate_qr_btn)
        
        layout.addStretch()
        
        return widget
    
    def create_manual_login_widget(self) -> QWidget:
        """创建手动登录界面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 说明
        info_label = QLabel(
            "手动登录说明：\n"
            "1. 打开米游社网页版并登录\n"
            "2. 按 F12 打开开发者工具\n"
            "3. 在 Console 中输入: document.cookie\n"
            "4. 复制完整的 Cookie 字符串粘贴到下方"
        )
        info_label.setStyleSheet("padding: 10px; background-color: #f0f0f0;")
        layout.addWidget(info_label)
        
        # Cookie 输入框
        cookie_label = QLabel("Cookie:")
        layout.addWidget(cookie_label)
        
        self.cookie_input = QTextEdit()
        self.cookie_input.setPlaceholderText("粘贴完整的 Cookie 字符串...")
        self.cookie_input.setMaximumHeight(150)
        layout.addWidget(self.cookie_input)
        
        # 登录按钮
        login_btn = QPushButton("登录")
        login_btn.clicked.connect(self.manual_login)
        layout.addWidget(login_btn)
        
        layout.addStretch()
        
        return widget
    
    def generate_qr_code(self):
        """生成二维码"""
        self.generate_qr_btn.setEnabled(False)
        self.generate_qr_btn.setText("生成中...")
        
        qr_url, ticket = self.auth_service.generate_qr_code()
        
        if qr_url and ticket:
            # 生成二维码图片
            qr_image = self.auth_service.create_qr_image(qr_url)
            
            # 使用临时文件保存二维码
            import tempfile
            import os
            temp_dir = tempfile.gettempdir()
            qr_path = os.path.join(temp_dir, 'mys_qr_code.png')
            qr_image.save(qr_path)
            
            # 显示二维码
            pixmap = QPixmap(qr_path)
            scaled_pixmap = pixmap.scaled(
                280, 280,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.qr_label.setPixmap(scaled_pixmap)
            
            # 开始检查登录状态
            self.check_thread = LoginCheckThread(self.auth_service, ticket)
            self.check_thread.start()
            
            self.generate_qr_btn.setText("等待扫码...")
        else:
            QMessageBox.warning(self, "错误", "生成二维码失败，请重试")
            self.generate_qr_btn.setEnabled(True)
            self.generate_qr_btn.setText("生成二维码")
    
    def manual_login(self):
        """手动登录"""
        cookie_str = self.cookie_input.toPlainText().strip()
        
        if not cookie_str:
            QMessageBox.warning(self, "提示", "请输入 Cookie")
            return
        
        cookies = self.auth_service.parse_manual_cookies(cookie_str)
        
        if cookies:
            device_id = uuid.uuid4().hex
            self.storage.save_cookies(cookies, device_id)
            logger.info("手动登录成功")
            self.login_success.emit()
        else:
            QMessageBox.warning(
                self,
                "登录失败",
                "Cookie 格式不正确或缺少必要字段\n\n"
                "请确保包含以下字段：\n"
                "- ltoken\n"
                "- ltuid\n"
                "- account_id\n"
                "- cookie_token\n"
                "- account_mid_v2"
            )
    
    def on_login_success(self, cookies: dict, device_id: str):
        """登录成功回调"""
        self.storage.save_cookies(cookies, device_id)
        logger.info("扫码登录成功")
        
        # 重置按钮状态
        self.generate_qr_btn.setEnabled(True)
        self.generate_qr_btn.setText("生成二维码")
        
        self.login_success.emit()
    
    def on_login_failed(self, error: str):
        """登录失败回调"""
        QMessageBox.warning(self, "登录失败", f"登录失败: {error}")
        
        self.generate_qr_btn.setEnabled(True)
        self.generate_qr_btn.setText("生成二维码")
