"""
Modern PyQt6 GUI for Voice Transcription
現代化語音轉錄 GUI 視窗
"""
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, 
    QPushButton, QLabel, QFrame, QDialog, QLineEdit,
    QListWidget, QListWidgetItem, QDialogButtonBox, QMenu, QApplication
)
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QLinearGradient, QPainterPath, QTextOption

# 全域配置
FONT_SIZE = 24  # 預設字體大小


class SelectableLabel(QTextEdit):
    """可選取文字的 Label，用於歷史句子列表"""
    
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setPlainText(text)
        self.setReadOnly(True)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        self.setSizeAdjustPolicy(QTextEdit.SizeAdjustPolicy.AdjustToContents)
        self.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
                font-size: 13px;
                font-family: 'Microsoft YaHei', 'Arial', sans-serif;
            }
        """)
        # 自動調整高度
        self.document().setDocumentMargin(0)
        self.setFixedHeight(self.get_text_height())
    
    def get_text_height(self):
        """計算文字所需的精確高度"""
        doc = self.document().clone()
        doc.setTextWidth(self.viewport().width() if self.viewport().width() > 0 else 500)
        height = doc.size().height()
        return int(height) + 2  # 加一點小邊距


class DragHandle(QWidget):
    """左側拖拽區塊，帶有斜線紋理"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(40)
        self.is_night_mode = False
        
    def set_night_mode(self, is_night):
        """設置夜間模式"""
        self.is_night_mode = is_night
        self.update()
        
    def paintEvent(self, event):
        """繪製帶有斜線紋理的拖拽區塊"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 背景：半透明
        bg_color = QColor(30, 30, 30, 180) if self.is_night_mode else QColor(255, 255, 255, 180)
        painter.fillRect(self.rect(), bg_color)
        
        # 繪製黃色斜線紋理
        pen = QPen(QColor(255, 193, 7, 255))  # 黃色，不透明
        pen.setWidth(2)
        painter.setPen(pen)
        
        spacing = 8
        for i in range(-self.height(), self.height(), spacing):
            painter.drawLine(0, i, self.width(), i + self.width())


class ThemeButton(QPushButton):
    """夜間模式切換按鈕"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(24, 24)
        self.setCheckable(True)
        self.setChecked(False)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("切換夜間模式")
        self.is_night_mode = False
        
    def set_night_mode(self, is_night):
        self.is_night_mode = is_night
        self.setChecked(is_night)
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 懸停效果
        if self.underMouse():
            painter.setBrush(QColor(255, 193, 7, 40))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(self.rect(), 4, 4)
            
        center = self.rect().center()
        
        if self.isChecked(): # Night Mode (Moon)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 255)) # White Moon
            
            path = QPainterPath()
            path.addEllipse(center.x() - 4, center.y() - 4, 8, 8)
            
            path2 = QPainterPath()
            path2.addEllipse(center.x() - 1, center.y() - 6, 8, 8)
            
            path = path.subtracted(path2)
            painter.drawPath(path)
        else: # Day Mode (Sun)
            painter.setPen(QPen(QColor(255, 193, 7), 1.5)) # Yellow Sun
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center, 4, 4)
            
            # Rays
            painter.save()
            painter.translate(center)
            for i in range(8):
                painter.rotate(45)
                painter.drawLine(0, 6, 0, 8)
            painter.restore()


class PinButton(QPushButton):
    """自定義繪製的釘選按鈕"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(24, 24)
        self.setCheckable(True)
        self.setChecked(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("釘選在最上層")
        self.is_night_mode = False

    def set_night_mode(self, is_night):
        self.is_night_mode = is_night
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 懸停效果
        if self.underMouse():
            painter.setBrush(QColor(255, 193, 7, 40))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(self.rect(), 4, 4)
            
        # 繪製圖標
        # Night mode: White when checked, Grey when unchecked? Or Yellow?
        # User said "icon and text become white".
        if self.is_night_mode:
             color = QColor(255, 255, 255) if self.isChecked() else QColor(100, 100, 100)
        else:
             color = QColor(255, 193, 7) if self.isChecked() else QColor(150, 150, 150)

        painter.setPen(QPen(color, 1.5))
        painter.setBrush(color if self.isChecked() else Qt.BrushStyle.NoBrush)
        
        # 座標變換
        center = self.rect().center()
        painter.translate(center)
        painter.rotate(-45)
        
        # 繪製圖釘形狀
        painter.drawEllipse(QPoint(0, -5), 3, 3)  # 頭部
        painter.drawLine(0, -2, 0, 6)         # 針身


class ModernButton(QPushButton):
    """現代化按鈕樣式"""
    
    def __init__(self, text, icon_text="", parent=None):
        super().__init__(text, parent)
        self.icon_text = icon_text
        self.is_night_mode = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_style()
        
    def set_night_mode(self, is_night):
        self.is_night_mode = is_night
        self.update_style()
        
    def update_style(self):
        text_color = "#FFFFFF" if self.is_night_mode else "#1a1a1a"
        hover_bg = "rgba(255, 255, 255, 0.1)" if self.is_night_mode else "rgba(255, 193, 7, 0.2)"
        pressed_bg = "rgba(255, 255, 255, 0.2)" if self.is_night_mode else "rgba(255, 193, 7, 0.4)"
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid #FFC107;
                border-radius: 4px;
                color: {text_color};
                font-weight: bold;
                font-size: 12px;
                padding: 2px 8px;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
            }}
            QPushButton:pressed {{
                background-color: {pressed_bg};
            }}
            QPushButton:disabled {{
                border: 1px solid #E0E0E0;
                color: #BDBDBD;
            }}
        """)


class ContentFrame(QFrame):
    """右側內容區塊，包含右下角調整大小的標示"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_night_mode = False
        
    def set_night_mode(self, is_night):
        self.is_night_mode = is_night
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 背景
        bg_color = QColor(30, 30, 30, 240) if self.is_night_mode else QColor(255, 255, 255, 240)
        painter.fillRect(self.rect(), bg_color)
        
        # 繪製右下角調整大小的斜線標示
        pen = QPen(QColor(255, 193, 7))
        pen.setWidth(2)
        painter.setPen(pen)
        
        w = self.width()
        h = self.height()
        
        # 繪製三條斜線
        for i in range(3):
            offset = (i + 1) * 5
            painter.drawLine(w - 2, h - 2 - offset, w - 2 - offset, h - 2)


class HistoryDialog(QDialog):
    """彈出式視窗：顯示所有歷史句子，支援搜尋與複製"""

    def __init__(self, sentences, is_night_mode=False, parent=None):
        super().__init__(parent)
        self.sentences = list(sentences) if sentences is not None else []
        self.is_night_mode = is_night_mode
        self.parent_window = parent  # 保存父視窗引用
        
        # 拖拽與調整大小相關
        self.drag_position = QPoint()
        self.resizing = False
        self.resize_margin = 10
        
        # 設置無邊框視窗
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Dialog
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)  # 啟用滑鼠追蹤以更改游標
        self.resize(600, 400)
        self.setMinimumSize(400, 300)
        
        self.init_ui()
        self.apply_theme()
        self.populate_list(scroll_to_bottom=True)  # 初始化填充列表並滾動到底部

    def init_ui(self):
        """初始化 UI"""
        # 主佈局
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 左側拖拽區塊
        self.drag_handle = DragHandle()
        main_layout.addWidget(self.drag_handle)
        
        # 右側內容區
        self.content_widget = self.create_content_area()
        main_layout.addWidget(self.content_widget)
        
        self.setLayout(main_layout)

    def create_content_area(self):
        """創建右側內容區"""
        content = ContentFrame()

        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)
        
        # 頂部標題和控制區
        top_layout = QHBoxLayout()
        
        # 標題
        self.title_label = QLabel("歷史紀錄")
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #1a1a1a;
            }
        """)
        top_layout.addWidget(self.title_label)
        top_layout.addStretch()
        
        # 夜間模式按鈕
        self.theme_btn = ThemeButton()
        self.theme_btn.set_night_mode(self.is_night_mode)
        self.theme_btn.clicked.connect(self.toggle_theme)
        top_layout.addWidget(self.theme_btn)
        
        # 關閉按鈕
        self.close_btn = ModernButton("✕")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setToolTip("關閉")
        self.close_btn.clicked.connect(self.reject)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #757575;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                color: #F44336;
                background-color: rgba(244, 67, 54, 0.1);
                border-radius: 4px;
            }
        """)
        top_layout.addWidget(self.close_btn)
        
        layout.addLayout(top_layout)
        
        # 搜尋輸入框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜尋句子...")
        self.search_input.textChanged.connect(self.on_search)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: 1px solid #FFC107;
                border-radius: 4px;
                color: #1a1a1a;
                font-size: 12px;
                padding: 5px;
            }
            QLineEdit:focus {
                border: 1px solid #FFD54F;
            }
        """)
        layout.addWidget(self.search_input)
        
        # 列表顯示 (每個句子獨立的 block)
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.list_widget.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.list_widget.setWordWrap(True)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.open_context_menu)
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: 1px solid #FFC107;
                border-radius: 4px;
                color: #1a1a1a;
                font-size: 13px;
                padding: 5px;
                font-family: 'Microsoft YaHei', 'Arial', sans-serif;
                outline: none;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px 0px;
                border-radius: 4px;
                border: none;
            }
            QListWidget::item:hover {
                background-color: rgba(255, 193, 7, 0.15);
            }
            QListWidget::item:selected {
                background-color: rgba(255, 193, 7, 0.4);
                color: #1a1a1a;
                border: none;
                outline: none;
            }
            QListWidget::item:focus {
                outline: none;
                border: none;
            }
        """)
        layout.addWidget(self.list_widget, 1)
        
        content.setLayout(layout)
        return content

    def populate_list(self, filter_text: str = "", scroll_to_bottom: bool = False):
        """將句子填入列表，根據搜尋文字過濾，新訊息在下方"""
        self.list_widget.clear()
        ft = filter_text.strip().lower()
        for s in self.sentences:  # 移除 reversed，讓新訊息在下方
            if not ft or ft in s.lower():
                item = QListWidgetItem(self.list_widget)
                # 創建可選取文字的 widget
                label = SelectableLabel(s)
                # 設置 item 的高度為內容高度 + padding
                item.setSizeHint(label.sizeHint())
                self.list_widget.addItem(item)
                self.list_widget.setItemWidget(item, label)
        
        # 只在指定時滾動到最底部
        if scroll_to_bottom:
            self.list_widget.scrollToBottom()

    def on_search(self, text: str):
        self.populate_list(text)
    
    def update_sentences(self, sentences):
        """更新句子列表（由父視窗調用）"""
        old_count = len(self.sentences)
        self.sentences = list(sentences)
        current_search = self.search_input.text()
        # 只有在新增句子時才滾動到底部
        scroll_to_bottom = len(self.sentences) > old_count and not current_search
        self.populate_list(current_search, scroll_to_bottom=scroll_to_bottom)

    def open_context_menu(self, point):
        """顯示右鍵選單"""
        item = self.list_widget.itemAt(point)
        if item is None:
            return
        
        # 獲取 item 中的 widget
        widget = self.list_widget.itemWidget(item)
        if widget is None:
            return
        
        menu = QMenu(self)
        
        # 檢查是否有選取文字
        if isinstance(widget, SelectableLabel):
            cursor = widget.textCursor()
            if cursor.hasSelection():
                # 有選取文字，複製選取的部分
                copy_action = menu.addAction("複製選取文字")
                copy_action.triggered.connect(lambda: QApplication.clipboard().setText(cursor.selectedText()))
            else:
                # 沒有選取文字，複製整句
                copy_action = menu.addAction("複製整句")
                copy_action.triggered.connect(lambda: QApplication.clipboard().setText(widget.toPlainText()))
        
        menu.exec(self.list_widget.mapToGlobal(point))
    
    def toggle_theme(self):
        """切換夜間模式"""
        self.is_night_mode = not self.is_night_mode
        self.theme_btn.set_night_mode(self.is_night_mode)
        self.apply_theme()
    
    def apply_theme(self):
        """應用主題樣式"""
        # 更新拖拽區塊
        self.drag_handle.set_night_mode(self.is_night_mode)
        
        # 更新內容區塊
        if isinstance(self.content_widget, ContentFrame):
            self.content_widget.set_night_mode(self.is_night_mode)
        
        # 顏色定義
        text_color = "#FFFFFF" if self.is_night_mode else "#1a1a1a"
        bg_color = "rgba(40, 40, 40, 0.95)" if self.is_night_mode else "rgba(255, 255, 255, 0.95)"
        border_color = "#FFC107"
        hover_bg = "rgba(255, 255, 255, 0.1)" if self.is_night_mode else "rgba(255, 193, 7, 0.1)"
        selected_bg = "rgba(255, 255, 255, 0.2)" if self.is_night_mode else "rgba(255, 193, 7, 0.3)"
        
        # 更新標題
        self.title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {text_color};
            }}
        """)
        
        # 更新搜尋框
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: transparent;
                border: 1px solid {border_color};
                border-radius: 4px;
                color: {text_color};
                font-size: 12px;
                padding: 5px;
            }}
            QLineEdit:focus {{
                border: 1px solid #FFD54F;
            }}
        """)
        
        # 更新列表顯示
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: 1px solid {border_color};
                border-radius: 4px;
                color: {text_color};
                font-size: 13px;
                padding: 5px;
                font-family: 'Microsoft YaHei', 'Arial', sans-serif;
                outline: none;
            }}
            QListWidget::item {{
                padding: 8px;
                margin: 2px 0px;
                border-radius: 4px;
                border: none;
            }}
            QListWidget::item:hover {{
                background-color: {hover_bg};
            }}
            QListWidget::item:selected {{
                background-color: {selected_bg};
                color: {text_color};
                border: none;
                outline: none;
            }}
            QListWidget::item:focus {{
                outline: none;
                border: none;
            }}
        """)
        
        # 更新關閉按鈕
        close_color = "#AAAAAA" if self.is_night_mode else "#757575"
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {close_color};
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                color: #F44336;
                background-color: rgba(244, 67, 54, 0.1);
                border-radius: 4px;
            }}
        """)
        
        # 重新填充列表以更新顯示
        current_search = self.search_input.text()
        self.populate_list(current_search)
    
    def mousePressEvent(self, event):
        """滑鼠按下事件 - 用於拖拽和調整大小"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 檢查是否在調整大小區域 (右下角)
            if self.check_resize_area(event.pos()):
                self.resizing = True
                self.resize_start_pos = event.globalPosition().toPoint()
                self.resize_start_size = self.size()
                event.accept()
                return

            # 檢查是否點擊在拖拽區域
            if self.drag_handle.geometry().contains(event.pos()):
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
    
    def mouseMoveEvent(self, event):
        """滑鼠移動事件 - 用於拖拽和調整大小"""
        # 更新游標形狀
        self.update_cursor(event.pos())

        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.resizing:
                # 調整大小邏輯
                delta = event.globalPosition().toPoint() - self.resize_start_pos
                new_width = max(self.minimumWidth(), self.resize_start_size.width() + delta.x())
                new_height = max(self.minimumHeight(), self.resize_start_size.height() + delta.y())
                self.resize(new_width, new_height)
                event.accept()
            elif not self.drag_position.isNull():
                # 移動視窗邏輯
                self.move(event.globalPosition().toPoint() - self.drag_position)
                event.accept()
    
    def mouseReleaseEvent(self, event):
        """滑鼠釋放事件"""
        self.drag_position = QPoint()
        self.resizing = False
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def check_resize_area(self, pos):
        """檢查滑鼠是否在調整大小區域 (右下角三角形區域)"""
        rect = self.rect()
        resize_grip_size = 20
        
        # 檢查是否在右下角區域
        if (pos.x() > rect.width() - resize_grip_size and 
            pos.y() > rect.height() - resize_grip_size):
            return True
        return False

    def update_cursor(self, pos):
        """根據滑鼠位置更新游標"""
        if self.check_resize_area(pos):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)


class TranscriptionWindow(QWidget):
    """主視窗類"""
    
    # 信號定義
    close_requested = pyqtSignal()
    pin_toggled = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        
        # 視窗屬性
        self.is_pinned = True
        self.is_live_mode = True
        self.is_night_mode = False
        self.font_size = FONT_SIZE
        self.current_index = 0
        self.sentences = []
        self.history_dialog = None  # 追蹤歷史視窗
        
        # 拖拽與調整大小相關
        self.drag_position = QPoint()
        self.resizing = False
        self.resize_margin = 10  # 調整大小的邊緣寬度
        
        self.init_ui()
        
    def init_ui(self):
        """初始化 UI"""
        # 設置無邊框視窗，並置頂
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)  # 啟用滑鼠追蹤以更改游標
        
        # 主佈局
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 左側拖拽區塊
        self.drag_handle = DragHandle()
        main_layout.addWidget(self.drag_handle)
        
        # 右側內容區
        self.content_widget = self.create_content_area()
        main_layout.addWidget(self.content_widget)
        
        self.setLayout(main_layout)
        
        # 設置視窗大小 (更窄的初始高度)
        self.setMinimumSize(400, 120)
        self.resize(600, 150)
        
    def create_content_area(self):
        """創建右側內容區"""
        content = ContentFrame()
        content.setStyleSheet("""
            QFrame {
                border: 1px solid #FFC107;
                border-left: none;
                border-radius: 0px 8px 8px 0px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(5)
        
        # 頂部控制區
        top_control = self.create_top_control()
        layout.addLayout(top_control)
        
        # 中間句子顯示區
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: transparent;
                border: none;
                color: #1a1a1a;
                font-size: {self.font_size}px;
                font-family: 'Microsoft YaHei', 'Arial', sans-serif;
                padding: 5px;
            }}
        """)
        self.text_display.setPlaceholderText("等待語音輸入...")
        layout.addWidget(self.text_display, 1)
        
        # 底部導航區
        bottom_nav = self.create_bottom_navigation()
        layout.addLayout(bottom_nav)
        
        content.setLayout(layout)
        return content
        
    def create_top_control(self):
        """創建頂部控制按鈕"""
        layout = QHBoxLayout()
        layout.setSpacing(5)
        
        layout.addStretch()
        
        # 夜間模式按鈕
        self.theme_btn = ThemeButton()
        self.theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_btn)

        # 歷史句子按鈕
        self.history_btn = ModernButton("歷史")
        self.history_btn.setFixedSize(60, 24)
        self.history_btn.setToolTip("顯示歷史句子")
        self.history_btn.clicked.connect(self.open_history_dialog)
        layout.addWidget(self.history_btn)
        
        # 釘選按鈕
        self.pin_btn = PinButton()
        self.pin_btn.clicked.connect(self.toggle_pin)
        layout.addWidget(self.pin_btn)
        
        # 關閉按鈕
        self.close_btn = ModernButton("✕")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setToolTip("關閉程式")
        self.close_btn.clicked.connect(self.close_window)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #757575;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                color: #F44336;
                background-color: rgba(244, 67, 54, 0.1);
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.close_btn)
        
        return layout
        
    def create_bottom_navigation(self):
        """創建底部導航按鈕"""
        layout = QHBoxLayout()
        layout.setSpacing(5)
        
        layout.addStretch()
        
        # 上一句按鈕
        self.prev_btn = ModernButton("◀")
        self.prev_btn.setFixedSize(28, 24)
        self.prev_btn.setToolTip("上一句")
        self.prev_btn.clicked.connect(self.show_previous)
        self.prev_btn.setEnabled(False)
        layout.addWidget(self.prev_btn)
        
        # 模式切換按鈕
        self.mode_btn = ModernButton("Auto")
        self.mode_btn.setFixedSize(60, 24)
        self.mode_btn.setToolTip("切換自動/手動模式")
        self.mode_btn.clicked.connect(self.toggle_mode)
        self.update_mode_button()
        layout.addWidget(self.mode_btn)
        
        # 下一句按鈕
        self.next_btn = ModernButton("▶")
        self.next_btn.setFixedSize(28, 24)
        self.next_btn.setToolTip("下一句")
        self.next_btn.clicked.connect(self.show_next)
        self.next_btn.setEnabled(False)
        layout.addWidget(self.next_btn)
        
        layout.addStretch()
        
        return layout
        
    def toggle_theme(self):
        """切換夜間模式"""
        self.is_night_mode = not self.is_night_mode
        self.theme_btn.set_night_mode(self.is_night_mode)
        self.apply_theme()
        
    def apply_theme(self):
        """應用主題樣式"""
        # 更新拖拽區塊
        self.drag_handle.set_night_mode(self.is_night_mode)
        
        # 更新內容區塊
        if isinstance(self.content_widget, ContentFrame):
            self.content_widget.set_night_mode(self.is_night_mode)
            
        # 更新文字顯示
        text_color = "#FFFFFF" if self.is_night_mode else "#1a1a1a"
        self.text_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: transparent;
                border: none;
                color: {text_color};
                font-size: {self.font_size}px;
                font-family: 'Microsoft YaHei', 'Arial', sans-serif;
                padding: 5px;
            }}
        """)
        
        # 更新按鈕
        self.pin_btn.set_night_mode(self.is_night_mode)
        self.history_btn.set_night_mode(self.is_night_mode)
        self.prev_btn.set_night_mode(self.is_night_mode)
        self.mode_btn.set_night_mode(self.is_night_mode)
        self.next_btn.set_night_mode(self.is_night_mode)
        
        # 更新關閉按鈕
        close_color = "#AAAAAA" if self.is_night_mode else "#757575"
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {close_color};
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                color: #F44336;
                background-color: rgba(244, 67, 54, 0.1);
                border-radius: 4px;
            }}
        """)

    def mousePressEvent(self, event):
        """滑鼠按下事件 - 用於拖拽和調整大小"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 檢查是否在調整大小區域 (右下角優先，然後是右邊和底邊)
            if self.check_resize_area(event.pos()):
                self.resizing = True
                self.resize_start_pos = event.globalPosition().toPoint()
                self.resize_start_size = self.size()
                event.accept()
                return

            # 檢查是否點擊在拖拽區域
            if self.drag_handle.geometry().contains(event.pos()):
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
                
    def mouseMoveEvent(self, event):
        """滑鼠移動事件 - 用於拖拽和調整大小"""
        # 更新游標形狀
        self.update_cursor(event.pos())

        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.resizing:
                # 調整大小邏輯
                delta = event.globalPosition().toPoint() - self.resize_start_pos
                new_width = max(self.minimumWidth(), self.resize_start_size.width() + delta.x())
                new_height = max(self.minimumHeight(), self.resize_start_size.height() + delta.y())
                self.resize(new_width, new_height)
                event.accept()
            elif not self.drag_position.isNull():
                # 移動視窗邏輯
                self.move(event.globalPosition().toPoint() - self.drag_position)
                event.accept()
            
    def mouseReleaseEvent(self, event):
        """滑鼠釋放事件"""
        self.drag_position = QPoint()
        self.resizing = False
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def check_resize_area(self, pos):
        """檢查滑鼠是否在調整大小區域 (僅右下角三角形區域)"""
        rect = self.rect()
        resize_grip_size = 20  # 調整大小區域的大小
        
        # 檢查是否在右下角區域
        if (pos.x() > rect.width() - resize_grip_size and 
            pos.y() > rect.height() - resize_grip_size):
            return True
        return False

    def update_cursor(self, pos):
        """根據滑鼠位置更新游標"""
        if self.check_resize_area(pos):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def toggle_pin(self):
        """切換釘選狀態"""
        self.is_pinned = not self.is_pinned
        
        if self.is_pinned:
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint | 
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.Tool
            )
            self.pin_btn.setToolTip("釘選在最上層")
        else:
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.Tool
            )
            self.pin_btn.setToolTip("取消釘選")
            
        self.show()  # 重新顯示視窗以應用新的 flags
        self.pin_toggled.emit(self.is_pinned)
        
    def toggle_mode(self):
        """切換自動/手動模式"""
        self.is_live_mode = not self.is_live_mode
        self.update_mode_button()
        self.update_navigation_buttons()
        
        if self.is_live_mode:
            # 切換回自動模式，顯示最新句子
            if self.sentences:
                self.current_index = len(self.sentences) - 1
                self.display_current_sentence()
                
    def update_mode_button(self):
        """更新模式按鈕顯示"""
        if self.is_live_mode:
            self.mode_btn.setText("Auto")
        else:
            self.mode_btn.setText("Manual")
            
    def update_navigation_buttons(self):
        """更新導航按鈕狀態"""
        if self.is_live_mode:
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
        else:
            self.prev_btn.setEnabled(self.current_index > 0)
            self.next_btn.setEnabled(self.current_index < len(self.sentences) - 1)
            
    def show_previous(self):
        """顯示上一句"""
        if self.current_index > 0:
            self.current_index -= 1
            self.display_current_sentence()
            self.update_navigation_buttons()
            
    def show_next(self):
        """顯示下一句"""
        if self.current_index < len(self.sentences) - 1:
            self.current_index += 1
            self.display_current_sentence()
            self.update_navigation_buttons()
            
    def display_current_sentence(self):
        """顯示當前句子"""
        if 0 <= self.current_index < len(self.sentences):
            sentence = self.sentences[self.current_index]
            self.text_display.setPlainText(sentence)
            
    def add_sentence(self, sentence: str):
        """添加新句子（從外部調用）"""
        self.sentences.append(sentence)
        
        if self.is_live_mode:
            self.current_index = len(self.sentences) - 1
            self.display_current_sentence()
            
        self.update_navigation_buttons()
        
        # 即時更新歷史視窗
        if self.history_dialog is not None and self.history_dialog.isVisible():
            self.history_dialog.update_sentences(self.sentences)
        
    def open_history_dialog(self):
        """打開歷史句子對話框"""
        # 如果已經有打開的視窗，就不再開新的
        if self.history_dialog is not None and self.history_dialog.isVisible():
            self.history_dialog.raise_()
            self.history_dialog.activateWindow()
            return
        
        self.history_dialog = HistoryDialog(self.sentences, self.is_night_mode, parent=self)
        self.history_dialog.finished.connect(self.on_history_dialog_closed)
        self.history_dialog.show()  # 使用 show() 而不是 exec() 以支援非模態對話框
    
    def on_history_dialog_closed(self):
        """歷史視窗關閉時清理引用"""
        self.history_dialog = None
        
    def close_window(self):
        """關閉視窗"""
        self.close_requested.emit()
        self.close()


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # 測試視窗
    window = TranscriptionWindow()
    window.show()
    
    # 模擬添加一些句子
    test_sentences = [
        "這是第一句測試文字",
        "這是第二句測試文字，內容稍微長一些",
        "第三句話用來測試顯示效果",
        "最後一句話，確認所有功能都正常運作"
    ]
    
    # 使用計時器模擬句子添加
    def add_test_sentence():
        if test_sentences:
            window.add_sentence(test_sentences.pop(0))
    
    timer = QTimer()
    timer.timeout.connect(add_test_sentence)
    timer.start(2000)  # 每2秒添加一句
    
    sys.exit(app.exec())
