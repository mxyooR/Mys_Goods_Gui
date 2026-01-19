"""
米游社商品兑换助手 - PyQt6 重构版
Author: mxyooR
Description: 用于自动兑换米游社商品的桌面应用
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow
from utils.logger import setup_logger

def main():
    setup_logger()
    
    app = QApplication(sys.argv)
    app.setApplicationName("米游社商品兑换助手")
    app.setOrganizationName("mxyooR")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
