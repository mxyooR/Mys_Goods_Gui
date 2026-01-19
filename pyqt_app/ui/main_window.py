"""主窗口"""
import os
import sys
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QTabWidget, QSystemTrayIcon,
                             QMenu, QMessageBox, QTextEdit, QDialog)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction
from ui.login_widget import LoginWidget
from ui.goods_widget import GoodsWidget
from ui.task_widget import TaskWidget
from ui.styles import GLOBAL_STYLE, get_status_style
from utils.storage import get_storage
from utils.logger import get_logger

logger = get_logger()

# 获取应用根目录
APP_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.storage = get_storage()
        self.init_ui()
        self.setup_tray()
        self.check_login_status()
    
    def init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("米游社商品兑换助手")
        self.setMinimumSize(900, 600)
        
        # 设置窗口图标
        icon_path = APP_DIR / 'tray_icon.ico'
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # 应用全局样式
        self.setStyleSheet(GLOBAL_STYLE)
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 顶部状态栏
        self.status_label = QLabel("未登录")
        self.status_label.setStyleSheet(get_status_style("error"))
        layout.addWidget(self.status_label)
        
        # 标签页
        self.tabs = QTabWidget()
        
        # 登录页
        self.login_widget = LoginWidget()
        self.login_widget.login_success.connect(self.on_login_success)
        self.tabs.addTab(self.login_widget, "登录")
        
        # 商品页
        self.goods_widget = GoodsWidget()
        self.tabs.addTab(self.goods_widget, "商品列表")
        
        # 任务页
        self.task_widget = TaskWidget()
        self.tabs.addTab(self.task_widget, "任务管理")
        
        layout.addWidget(self.tabs)
        
        # 底部按钮栏
        bottom_widget = QWidget()
        bottom_widget.setStyleSheet("background-color: #f8f9fa; padding: 10px;")
        bottom_layout = QHBoxLayout(bottom_widget)
        
        self.refresh_btn = QPushButton("刷新状态")
        self.refresh_btn.clicked.connect(self.check_login_status)
        bottom_layout.addWidget(self.refresh_btn)
        
        self.view_log_btn = QPushButton("查看日志")
        self.view_log_btn.clicked.connect(self.view_log)
        bottom_layout.addWidget(self.view_log_btn)
        
        self.open_data_btn = QPushButton("打开数据目录")
        self.open_data_btn.clicked.connect(self.open_data_folder)
        bottom_layout.addWidget(self.open_data_btn)
        
        bottom_layout.addStretch()
        
        self.about_btn = QPushButton("关于")
        self.about_btn.clicked.connect(self.show_about)
        bottom_layout.addWidget(self.about_btn)
        
        layout.addWidget(bottom_widget)
    
    def setup_tray(self):
        """设置系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # 设置托盘图标
        icon_path = APP_DIR / 'tray_icon.png'
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
        
        tray_menu = QMenu()
        
        show_action = QAction("显示", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        # 显示托盘图标
        if icon_path.exists():
            self.tray_icon.show()
            self.tray_icon.setToolTip("米游社商品兑换助手")
    
    def on_tray_activated(self, reason):
        """托盘图标点击事件"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()
    
    def check_login_status(self):
        """检查登录状态"""
        cookies = self.storage.get_cookies()
        if cookies and 'account_id' in cookies:
            account_id = cookies.get('account_id', '')
            self.status_label.setText(f"已登录 - 账号ID: {account_id}")
            self.status_label.setStyleSheet(get_status_style("success"))
            
            # 启用其他标签页
            self.tabs.setTabEnabled(1, True)
            self.tabs.setTabEnabled(2, True)
        else:
            self.status_label.setText("未登录 - 请先登录")
            self.status_label.setStyleSheet(get_status_style("error"))
            
            # 禁用其他标签页
            self.tabs.setTabEnabled(1, False)
            self.tabs.setTabEnabled(2, False)
    
    def on_login_success(self):
        """登录成功回调"""
        self.check_login_status()
        QMessageBox.information(self, "成功", "登录成功！")
        self.tabs.setCurrentIndex(1)  # 切换到商品页
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于",
            "米游社商品兑换助手 v2.0\n\n"
            "PyQt6 重构版\n"
            "作者: mxyooR\n\n"
            "仅供学习使用，请勿用于非法用途"
        )
    
    def view_log(self):
        """查看日志"""
        app_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        log_file = app_dir / 'logs' / 'app.log'
        
        if not log_file.exists():
            QMessageBox.information(self, "提示", "日志文件不存在")
            return
        
        # 创建日志查看对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("日志查看")
        dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                text_edit.setPlainText(f.read())
            # 滚动到底部
            text_edit.verticalScrollBar().setValue(
                text_edit.verticalScrollBar().maximum()
            )
        except Exception as e:
            text_edit.setPlainText(f"读取日志失败: {e}")
        
        layout.addWidget(text_edit)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(lambda: self._refresh_log(text_edit, log_file))
        button_layout.addWidget(refresh_btn)
        
        clear_btn = QPushButton("清空日志")
        clear_btn.clicked.connect(lambda: self._clear_log(log_file, text_edit))
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def _refresh_log(self, text_edit, log_file):
        """刷新日志内容"""
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                text_edit.setPlainText(f.read())
            text_edit.verticalScrollBar().setValue(
                text_edit.verticalScrollBar().maximum()
            )
        except Exception as e:
            QMessageBox.warning(self, "错误", f"刷新日志失败: {e}")
    
    def _clear_log(self, log_file, text_edit):
        """清空日志"""
        reply = QMessageBox.question(
            self,
            "确认",
            "确定要清空日志吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write('')
                text_edit.clear()
                QMessageBox.information(self, "成功", "日志已清空")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"清空日志失败: {e}")
    
    def open_data_folder(self):
        """打开数据目录"""
        data_dir = self.storage.data_dir
        
        if not data_dir.exists():
            QMessageBox.warning(self, "提示", "数据目录不存在")
            return
        
        try:
            # 跨平台打开文件夹
            if sys.platform == 'win32':
                os.startfile(data_dir)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', data_dir])
            else:  # Linux
                subprocess.run(['xdg-open', data_dir])
        except Exception as e:
            QMessageBox.warning(self, "错误", f"打开目录失败: {e}")
    
    def closeEvent(self, event):
        """关闭事件"""
        reply = QMessageBox.question(
            self,
            "确认",
            "是否最小化到托盘？\n\n点击「是」最小化到托盘\n点击「否」退出程序",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.ignore()
            self.hide()
        elif reply == QMessageBox.StandardButton.No:
            self.quit_app()
        else:
            event.ignore()
    
    def quit_app(self):
        """退出应用"""
        # 停止所有运行中的任务
        self.task_widget.stop_all_tasks()
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
        from PyQt6.QtWidgets import QApplication
        QApplication.instance().quit()
