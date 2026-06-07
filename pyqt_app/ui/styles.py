"""UI 样式定义 - 工作台风格"""

PRIMARY_COLOR = "#2563eb"
PRIMARY_HOVER = "#1d4ed8"
SUCCESS_BG = "#16a34a"
SUCCESS_TEXT = "#ffffff"

BG_WHITE = "#ffffff"
BG_LIGHT = "#f6f8fb"

TEXT_PRIMARY = "#172033"
TEXT_SECONDARY = "#64748b"

BORDER_COLOR = "#d8dee9"

GLOBAL_STYLE = """
QWidget {
    font-family: "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
    font-size: 14px;
    color: #172033;
}

QMainWindow {
    background-color: #f6f8fb;
}

QWidget#bottomBar {
    background-color: #ffffff;
    border-top: 1px solid #d8dee9;
}

QLabel#statusBanner {
    border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

QTabWidget::pane {
    border: none;
    background-color: #ffffff;
    border-top: 1px solid #e5eaf2;
}

QTabBar::tab {
    background-color: #eef2f7;
    color: #475569;
    padding: 12px 26px;
    margin: 0 2px 0 0;
    border: none;
    border-bottom: 3px solid transparent;
    font-size: 14px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #2563eb;
    border-bottom: 3px solid #2563eb;
    font-weight: bold;
}

QTabBar::tab:hover {
    background-color: #e2e8f0;
}

QTabBar::tab:disabled {
    color: #94a3b8;
}

QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    padding: 9px 16px;
    border-radius: 6px;
    font-size: 14px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #1d4ed8;
}

QPushButton:pressed {
    background-color: #1e40af;
}

QPushButton:disabled {
    background-color: #cbd5e1;
    color: #f8fafc;
}

QPushButton#secondaryButton {
    background-color: #eef2f7;
    color: #334155;
    border: 1px solid #d8dee9;
}

QPushButton#secondaryButton:hover {
    background-color: #e2e8f0;
}

QPushButton#dangerButton {
    background-color: #dc2626;
}

QPushButton#dangerButton:hover {
    background-color: #b91c1c;
}

QPushButton#successButton {
    background-color: #16a34a;
}

QPushButton#successButton:hover {
    background-color: #15803d;
}

QLineEdit, QTextEdit, QSpinBox, QComboBox, QDateTimeEdit {
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px 12px;
    background-color: #ffffff;
    font-size: 14px;
}

QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus, QDateTimeEdit:focus {
    border: 1px solid #2563eb;
    outline: none;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #172033;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    border: 1px solid #cbd5e1;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
    background-color: #ffffff;
    font-size: 14px;
}

QTableWidget {
    border: 1px solid #d8dee9;
    border-radius: 6px;
    background-color: #ffffff;
    gridline-color: #edf1f7;
    font-size: 14px;
    alternate-background-color: #f8fafc;
}

QTableWidget::item {
    padding: 10px;
    border-bottom: 1px solid #edf1f7;
}

QTableWidget::item:selected {
    background-color: #dbeafe;
    color: #172033;
}

QTableWidget QWidget QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 13px;
    min-height: 28px;
}

QTableWidget QWidget QPushButton:hover {
    background-color: #1d4ed8;
}

QTableWidget QWidget QPushButton:disabled {
    background-color: #cbd5e1;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #f1f5f9;
    color: #172033;
    padding: 12px;
    border: none;
    border-bottom: 1px solid #d8dee9;
    font-weight: bold;
    text-align: center;
    font-size: 14px;
}

QLabel {
    color: #172033;
    font-size: 14px;
}

QLabel#pointsLabel {
    color: #2563eb;
    font-size: 16px;
    font-weight: bold;
    padding: 6px 10px;
}

QLabel#imagePlaceholder {
    border: 1px solid #d8dee9;
    border-radius: 6px;
    background-color: #f8fafc;
    color: #64748b;
}

QTextEdit#logView {
    font-family: Consolas, "Microsoft YaHei", monospace;
    font-size: 12px;
    background-color: #0f172a;
    color: #dbeafe;
    border: 1px solid #1e293b;
}

QScrollBar:vertical {
    border: none;
    background-color: #f1f5f9;
    width: 10px;
}

QScrollBar::handle:vertical {
    background-color: #94a3b8;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #64748b;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background-color: #f1f5f9;
    height: 10px;
}

QScrollBar::handle:horizontal {
    background-color: #94a3b8;
    border-radius: 5px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #64748b;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QDialog {
    background-color: #ffffff;
}
"""

def get_status_style(status_type="info"):
    """获取状态标签样式"""
    base = "padding: 12px 20px; color: #ffffff; font-size: 14px; font-weight: bold;"
    if status_type == "success":
        return base + "background-color: #16a34a;"
    if status_type == "error":
        return base + "background-color: #dc2626;"
    if status_type == "warning":
        return "padding: 12px 20px; background-color: #f59e0b; color: #172033; font-size: 14px; font-weight: bold;"
    return base + "background-color: #0891b2;"
