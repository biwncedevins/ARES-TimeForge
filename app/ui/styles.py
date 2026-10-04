"""Design system for TimeForge. Pure dark / black forensics tool."""

from app.utils.theme import (
    ACCENT,
    ACCENT_DIM,
    BG,
    BORDER,
    DANGER,
    OK,
    PANEL,
    PANEL2,
    SELECTED_BG,
    TEXT,
    TEXT_DIM,
    TEXT_FAINT,
)

STYLESHEET = f"""
* {{
    font-family: 'Segoe UI', 'Segoe UI Variable', sans-serif;
    font-size: 13px;
    color: {TEXT};
}}

QMainWindow, QWidget#AppRoot {{
    background-color: {BG};
}}

QLabel {{
    background: transparent;
}}

QLabel#BrandTitle {{
    font-size: 17px;
    font-weight: 700;
    letter-spacing: 2px;
    color: {TEXT};
}}

QLabel#BrandTagline {{
    font-size: 10px;
    letter-spacing: 3px;
    color: {TEXT_DIM};
}}

QLabel#SectionLabel {{
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
    color: {TEXT_DIM};
    text-transform: uppercase;
}}

QLabel#KeyLabel {{
    color: {TEXT_DIM};
    font-size: 12px;
}}

QLabel#ValueLabel {{
    font-family: Consolas, monospace;
    font-size: 12.5px;
    color: {TEXT};
}}

QLabel#ValueAccent {{
    font-family: Consolas, monospace;
    font-size: 13px;
    font-weight: 600;
    color: {ACCENT};
}}

QLabel#ValueDanger {{
    font-family: Consolas, monospace;
    font-size: 12.5px;
    color: {DANGER};
}}

QLabel#ValueOk {{
    font-family: Consolas, monospace;
    font-size: 12.5px;
    color: {OK};
}}

QLabel#EmptyHint {{
    color: {TEXT_FAINT};
}}

QLabel#Explainer {{
    font-size: 12px;
    color: {TEXT_DIM};
}}

QLineEdit, QPlainTextEdit {{
    background-color: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 7px 9px;
    selection-background-color: {ACCENT_DIM};
    selection-color: {TEXT};
}}

QLineEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {ACCENT_DIM};
}}

QLineEdit#InputField {{
    font-family: Consolas, monospace;
    font-size: 14px;
    padding: 10px 12px;
}}

QComboBox {{
    background-color: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 6px 10px;
}}

QComboBox::drop-down {{
    border: none;
    width: 22px;
}}

QComboBox QAbstractItemView {{
    background-color: {PANEL2};
    border: 1px solid {BORDER};
    selection-background-color: {ACCENT_DIM};
    selection-color: {TEXT};
}}

QPushButton {{
    background-color: {PANEL2};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 7px 16px;
    color: {TEXT};
}}

QPushButton:hover {{
    border: 1px solid {ACCENT_DIM};
}}

QPushButton:pressed {{
    background-color: {SELECTED_BG};
}}

QPushButton:disabled {{
    color: {TEXT_FAINT};
    border-color: {BORDER};
}}

QPushButton#PrimaryButton {{
    background-color: {SELECTED_BG};
    border: 1px solid {ACCENT_DIM};
    color: {ACCENT};
    font-weight: 600;
}}

QPushButton#PrimaryButton:hover {{
    border: 1px solid {ACCENT};
}}

QPushButton#SideButton {{
    text-align: left;
    padding: 10px 16px;
    border: none;
    border-left: 3px solid transparent;
    border-radius: 0;
    background: transparent;
    color: {TEXT_DIM};
    font-size: 13px;
}}

QPushButton#SideButton:hover {{
    color: {TEXT};
    background-color: {PANEL2};
}}

QPushButton#SideButton:checked {{
    color: {ACCENT};
    border-left: 3px solid {ACCENT};
    background-color: {SELECTED_BG};
}}

QPushButton#TopButton {{
    background: transparent;
    border: none;
    color: {TEXT_DIM};
    padding: 8px 12px;
    font-size: 12px;
}}

QPushButton#TopButton:hover {{
    color: {TEXT};
}}

QFrame#TopBar {{
    background-color: {BG};
    border-bottom: 1px solid {BORDER};
}}

QFrame#SideBar {{
    background-color: {PANEL};
    border-right: 1px solid {BORDER};
}}

QFrame#Panel {{
    background-color: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 4px;
}}

QFrame#PanelInner {{
    background-color: transparent;
    border: none;
}}

QScrollArea {{
    background: transparent;
    border: none;
}}

QScrollArea > QWidget > QWidget {{
    background: transparent;
}}

QScrollBar:vertical {{
    background: {BG};
    width: 10px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {BORDER};
    min-height: 24px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical:hover {{
    background: {TEXT_FAINT};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background: {BG};
    height: 10px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background: {BORDER};
    min-width: 24px;
    border-radius: 5px;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

QTableWidget {{
    background-color: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 4px;
    gridline-color: {BORDER};
    selection-background-color: {SELECTED_BG};
    selection-color: {TEXT};
    alternate-background-color: {BG};
}}

QHeaderView::section {{
    background-color: {PANEL2};
    color: {TEXT_DIM};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 6px 8px;
    font-size: 11px;
    font-weight: 600;
}}

QTableWidget::item {{
    padding: 4px 8px;
}}

QStatusBar {{
    background-color: {PANEL};
    color: {TEXT_DIM};
    border-top: 1px solid {BORDER};
}}

QToolTip {{
    background-color: {PANEL2};
    color: {TEXT};
    border: 1px solid {ACCENT_DIM};
}}

QCheckBox {{
    color: {TEXT_DIM};
}}
"""