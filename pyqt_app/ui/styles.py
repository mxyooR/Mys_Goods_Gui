"""UI 样式定义 - 简洁风格"""

# 主题色 - 简洁蓝色
PRIMARY_COLOR = "#007bff"
PRIMARY_HOVER = "#0069d9"
SUCCESS_BG = "#28a745"
SUCCESS_TEXT = "#ffffff"

# 背景色
BG_WHITE = "#ffffff"
BG_LIGHT = "#f8f9fa"

# 文字色
TEXT_PRIMARY = "#212529"
TEXT_SECONDARY = "#6c757d"

# 边框
BORDER_COLOR = "#dee2e6"

# 全局样式 - 简洁版
GLOBAL_STYLE = """
QWidget {
    font-family: "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
    font-size: 14px;
    color: #212529;
}

QMainWindow {
    background-color: #ffffff;
}

/* 标签页 - 简洁风格 */
QTabWidget::pane {
    border: none;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #f8f9fa;
    color: #495057;
    padding: 12px 24px;
    margin-right: 2px;
    border: none;
    border-bottom: 3px solid transparent;
    font-size: 14px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #007bff;
    border-bottom: 3px solid #007bff;
    font-weight: bold;
}

QTabBar::tab:hover {
    background-color: #e9ecef;
}

/* 按钮 - 扁平风格 */
QPushButton {
    background-color: #007bff;
    color: #ffffff;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #0069d9;
}

QPushButton:pressed {
    background-color: #0056b3;
}

QPushButton:disabled {
    background-color: #6c757d;
    color: #adb5bd;
}

/* 输入框 - 简洁边框 */
QLineEdit, QTextEdit, QSpinBox, QComboBox, QDateTimeEdit {
    border: 1px solid #ced4da;
    border-radius: 4px;
    padding: 8px 12px;
    background-color: #ffffff;
    font-size: 14px;
}

QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus, QDateTimeEdit:focus {
    border: 1px solid #80bdff;
    outline: none;
}

/* 下拉框 */
QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #212529;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    border: 1px solid #ced4da;
    selection-background-color: #007bff;
    selection-color: #ffffff;
    background-color: #ffffff;
    font-size: 14px;
}

/* 表格 - 清爽风格 */
QTableWidget {
    border: 1px solid #dee2e6;
    background-color: #ffffff;
    gridline-color: #dee2e6;
    font-size: 14px;
}

QTableWidget::item {
    padding: 10px;
    border-bottom: 1px solid #dee2e6;
}

QTableWidget::item:selected {
    background-color: #e7f3ff;
    color: #212529;
}

/* 表格内的按钮 - 确保文字可见 */
QTableWidget QWidget QPushButton {
    background-color: #007bff;
    color: #ffffff;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 13px;
    min-height: 28px;
}

QTableWidget QWidget QPushButton:hover {
    background-color: #0069d9;
}

QTableWidget QWidget QPushButton:disabled {
    background-color: #6c757d;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #f8f9fa;
    color: #212529;
    padding: 12px;
    border: none;
    border-bottom: 2px solid #dee2e6;
    font-weight: bold;
    text-align: center;
    font-size: 14px;
}

/* 标签 */
QLabel {
    color: #212529;
    font-size: 14px;
}

/* 滚动条 - 简洁 */
QScrollBar:vertical {
    border: none;
    background-color: #f8f9fa;
    width: 10px;
}

QScrollBar::handle:vertical {
    background-color: #adb5bd;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #6c757d;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background-color: #f8f9fa;
    height: 10px;
}

QScrollBar::handle:horizontal {
    background-color: #adb5bd;
    border-radius: 5px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #6c757d;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* 对话框 */
QDialog {
    background-color: #ffffff;
}
"""

# 状态标签样式 - 简洁版
def get_status_style(status_type="info"):
    """获取状态标签样式"""
    if status_type == "success":
        return "padding: 12px 20px; background-color: #28a745; color: #ffffff; font-size: 14px; font-weight: bold;"
    elif status_type == "error":
        return "padding: 12px 20px; background-color: #dc3545; color: #ffffff; font-size: 14px; font-weight: bold;"
    elif status_type == "warning":
        return "padding: 12px 20px; background-color: #ffc107; color: #212529; font-size: 14px; font-weight: bold;"
    else:
        return "padding: 12px 20px; background-color: #17a2b8; color: #ffffff; font-size: 14px; font-weight: bold;"

