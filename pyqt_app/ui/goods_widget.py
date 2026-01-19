"""商品列表界面"""
import requests
from io import BytesIO
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QComboBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
from core.goods import GoodsService
from core.auth import AuthService
from utils.storage import get_storage
from utils.logger import get_logger

logger = get_logger()

class GoodsWidget(QWidget):
    """商品列表界面"""
    
    def __init__(self):
        super().__init__()
        self.storage = get_storage()
        self.goods_service = GoodsService()
        self.current_goods = []
        self.init_ui()
    
    def init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)
        
        # 顶部控制栏
        top_layout = QHBoxLayout()
        
        # 游戏选择
        top_layout.addWidget(QLabel("选择游戏:"))
        self.game_combo = QComboBox()
        self.game_combo.currentTextChanged.connect(self.on_game_changed)
        top_layout.addWidget(self.game_combo)
        
        # 刷新按钮
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.load_goods)
        top_layout.addWidget(refresh_btn)
        
        top_layout.addStretch()
        
        # 米游币显示
        self.points_label = QLabel("米游币: --")
        self.points_label.setStyleSheet("font-weight: bold; padding: 5px; font-size: 16px; color: #007bff;")
        top_layout.addWidget(self.points_label)
        
        layout.addLayout(top_layout)
        
        # 商品表格
        self.goods_table = QTableWidget()
        self.goods_table.setColumnCount(7)
        self.goods_table.setHorizontalHeaderLabels([
            "图标", "商品名称", "价格", "兑换时间", "操作", "ID", "图标URL"
        ])
        
        # 隐藏 ID 和图标URL列
        self.goods_table.setColumnHidden(5, True)
        self.goods_table.setColumnHidden(6, True)
        
        # 设置列宽
        header = self.goods_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # 图标列固定宽度
        self.goods_table.setColumnWidth(0, 80)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # 商品名称自适应
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # 价格固定
        self.goods_table.setColumnWidth(2, 100)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # 时间固定
        self.goods_table.setColumnWidth(3, 160)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # 操作按钮固定
        self.goods_table.setColumnWidth(4, 120)
        
        # 设置行高
        self.goods_table.verticalHeader().setDefaultSectionSize(90)
        self.goods_table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.goods_table)
        
        # 底部按钮
        bottom_layout = QHBoxLayout()
        
        clear_wishlist_btn = QPushButton("清空心愿单")
        clear_wishlist_btn.setStyleSheet("background-color: #dc3545;")
        clear_wishlist_btn.clicked.connect(self.clear_wishlist)
        bottom_layout.addWidget(clear_wishlist_btn)
        
        bottom_layout.addStretch()
        
        layout.addLayout(bottom_layout)
        
        # 加载游戏列表
        self.load_games()
    
    def load_games(self):
        """加载游戏列表"""
        games = self.goods_service.get_game_list()
        if games:
            self.game_combo.clear()
            for game in games:
                self.game_combo.addItem(game['name'], game['key'])
            logger.info(f"加载了 {len(games)} 个游戏")
    
    def on_game_changed(self):
        """游戏切换事件"""
        self.load_goods()
    
    def load_goods(self):
        """加载商品列表"""
        game_key = self.game_combo.currentData()
        if not game_key:
            return
        
        # 获取 Cookie
        cookies = self.storage.get_cookies()
        cookie_str = AuthService.cookies_to_string(cookies)
        
        # 获取米游币
        points = self.goods_service.get_user_points(cookie_str)
        if points is not None:
            self.points_label.setText(f"米游币: {points}")
        
        # 获取商品列表
        goods = self.goods_service.get_goods_list(game_key, cookie_str)
        if goods:
            self.current_goods = goods
            self.display_goods(goods)
            logger.info(f"加载了 {len(goods)} 个商品")
        else:
            QMessageBox.warning(self, "提示", "获取商品列表失败")
    
    def display_goods(self, goods: list):
        """显示商品列表"""
        self.goods_table.setRowCount(len(goods))
        
        for row, item in enumerate(goods):
            # 商品图标
            icon_label = QLabel()
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setFixedSize(70, 70)
            icon_label.setStyleSheet("border: 1px solid #dee2e6; border-radius: 35px;")
            
            # 异步加载图片
            icon_url = item.get('icon', '')
            if icon_url:
                try:
                    response = requests.get(icon_url, timeout=3)
                    if response.status_code == 200:
                        pixmap = QPixmap()
                        pixmap.loadFromData(response.content)
                        scaled_pixmap = pixmap.scaled(
                            70, 70,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                        icon_label.setPixmap(scaled_pixmap)
                except Exception as e:
                    logger.error(f"加载图片失败: {e}")
                    icon_label.setText("无图")
            else:
                icon_label.setText("无图")
            
            self.goods_table.setCellWidget(row, 0, icon_label)
            
            # 商品名称
            name_item = QTableWidgetItem(item.get('name', ''))
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.goods_table.setItem(row, 1, name_item)
            
            # 价格
            price = item.get('price', 0)
            price_item = QTableWidgetItem(f"{price} 币")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.goods_table.setItem(row, 2, price_item)
            
            # 兑换时间
            time_str = item.get('time', '未知')
            time_item = QTableWidgetItem(time_str)
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.goods_table.setItem(row, 3, time_item)
            
            # 操作按钮
            add_btn = QPushButton("加入心愿单")
            add_btn.setStyleSheet("""
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
            add_btn.clicked.connect(lambda checked, r=row: self.add_to_wishlist(r))
            self.goods_table.setCellWidget(row, 4, add_btn)
            
            # ID（隐藏）
            self.goods_table.setItem(row, 5, QTableWidgetItem(str(item.get('id', ''))))
            
            # 图标URL（隐藏）
            self.goods_table.setItem(row, 6, QTableWidgetItem(item.get('icon', '')))
    
    def add_to_wishlist(self, row: int):
        """添加到心愿单"""
        if row >= len(self.current_goods):
            return
        
        goods = self.current_goods[row]
        game_key = self.game_combo.currentData()
        
        wishlist_item = {
            'name': goods['name'],
            'id': goods['id'],
            'time': goods['time'],
            'biz': game_key
        }
        
        self.storage.add_to_wishlist(wishlist_item)
        logger.info(f"已添加到心愿单: {goods['name']}")
        QMessageBox.information(self, "成功", f"已添加到心愿单: {goods['name']}")
    
    def clear_wishlist(self):
        """清空心愿单"""
        reply = QMessageBox.question(
            self,
            "确认",
            "确定要清空心愿单吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.storage.clear_wishlist()
            logger.info("心愿单已清空")
            QMessageBox.information(self, "成功", "心愿单已清空")
