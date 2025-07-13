#!/usr/bin/env python
"""
WordCloud GUI - 实时调整和预览词云生成
=====================================
基于PyQt5的GUI界面，支持实时调整参数和预览词云效果
支持高分屏显示和黑夜模式
"""

import sys
import os
import platform
import json
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QSlider, QSpinBox, 
                             QComboBox, QPushButton, QFileDialog, QGroupBox, 
                             QCheckBox, QTextEdit, QSplitter, QFrame, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from word_frequencies import word_frequencies


class WordCloudCanvas(FigureCanvas):
    """词云显示画布"""
    
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        
        # 设置高分屏支持
        self.fig.set_size_inches(width, height)
        self.fig.tight_layout()
        
    def update_wordcloud(self, wc, title="WordCloud"):
        """更新词云显示"""
        self.axes.clear()
        self.axes.imshow(wc, interpolation="bilinear")
        self.axes.set_title(title, fontsize=12, fontweight='bold')
        self.axes.axis('off')
        self.fig.tight_layout()
        self.draw()


class WordCloudGUI(QMainWindow):
    """词云生成器GUI主窗口"""
    
    def __init__(self):
        super().__init__()
        self.dark_mode = False
        self.current_word_frequencies = word_frequencies
        self.init_ui()
        self.init_data()
        self.setup_connections()
        self.apply_theme()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("WordCloud 生成器 - 实时预览")
        self.setGeometry(100, 100, 1400, 900)
        
        # 设置高分屏支持
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧控制面板
        control_panel = self.create_control_panel()
        splitter.addWidget(control_panel)
        
        # 右侧预览区域
        preview_panel = self.create_preview_panel()
        splitter.addWidget(preview_panel)
        
        # 设置分割器比例
        splitter.setSizes([400, 1000])
        
    def create_control_panel(self):
        """创建控制面板"""
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        
        # 主题切换按钮
        theme_layout = QHBoxLayout()
        self.theme_btn = QPushButton("🌙 黑夜模式")
        self.theme_btn.setCheckable(True)
        theme_layout.addWidget(self.theme_btn)
        theme_layout.addStretch()
        control_layout.addLayout(theme_layout)
        
        # 文件选择组
        file_group = QGroupBox("文件设置")
        file_layout = QVBoxLayout(file_group)
        
        # 词频文件选择
        self.freq_btn = QPushButton("选择词频文件")
        self.freq_label = QLabel("使用默认词频")
        file_layout.addWidget(self.freq_btn)
        file_layout.addWidget(self.freq_label)
        
        # 图片文件选择
        self.mask_btn = QPushButton("选择遮罩图片")
        self.mask_label = QLabel("未选择文件")
        file_layout.addWidget(self.mask_btn)
        file_layout.addWidget(self.mask_label)
        
        # 颜色图片选择
        self.color_btn = QPushButton("选择颜色图片")
        self.color_label = QLabel("未选择文件")
        file_layout.addWidget(self.color_btn)
        file_layout.addWidget(self.color_label)
        
        control_layout.addWidget(file_group)
        
        # 词云参数组
        params_group = QGroupBox("词云参数")
        params_layout = QGridLayout(params_group)
        
        # 最大词数
        params_layout.addWidget(QLabel("最大词数:"), 0, 0)
        self.max_words_spin = QSpinBox()
        self.max_words_spin.setRange(100, 10000)
        self.max_words_spin.setValue(1000)
        params_layout.addWidget(self.max_words_spin, 0, 1)
        
        # 最大字体大小
        params_layout.addWidget(QLabel("最大字体:"), 1, 0)
        self.max_font_spin = QSpinBox()
        self.max_font_spin.setRange(10, 200)
        self.max_font_spin.setValue(30)
        params_layout.addWidget(self.max_font_spin, 1, 1)
        
        # 最小字体大小
        params_layout.addWidget(QLabel("最小字体:"), 2, 0)
        self.min_font_spin = QSpinBox()
        self.min_font_spin.setRange(1, 50)
        self.min_font_spin.setValue(1)
        params_layout.addWidget(self.min_font_spin, 2, 1)
        
        # 相对缩放
        params_layout.addWidget(QLabel("相对缩放:"), 3, 0)
        self.relative_scaling_slider = QSlider(Qt.Horizontal)
        self.relative_scaling_slider.setRange(0, 100)
        self.relative_scaling_slider.setValue(10)
        params_layout.addWidget(self.relative_scaling_slider, 3, 1)
        self.relative_scaling_label = QLabel("0.1")
        params_layout.addWidget(self.relative_scaling_label, 3, 2)
        
        # 水平偏好
        params_layout.addWidget(QLabel("水平偏好:"), 4, 0)
        self.horizontal_slider = QSlider(Qt.Horizontal)
        self.horizontal_slider.setRange(0, 100)
        self.horizontal_slider.setValue(70)
        params_layout.addWidget(self.horizontal_slider, 4, 1)
        self.horizontal_label = QLabel("0.7")
        params_layout.addWidget(self.horizontal_label, 4, 2)
        
        # 边距
        params_layout.addWidget(QLabel("边距:"), 5, 0)
        self.margin_spin = QSpinBox()
        self.margin_spin.setRange(0, 50)
        self.margin_spin.setValue(10)
        params_layout.addWidget(self.margin_spin, 5, 1)
        
        control_layout.addWidget(params_group)
        
        # 颜色设置组
        color_group = QGroupBox("颜色设置")
        color_layout = QVBoxLayout(color_group)
        
        # 颜色模式选择
        self.color_mode_combo = QComboBox()
        self.color_mode_combo.addItems(["默认颜色", "灰度", "图片颜色"])
        color_layout.addWidget(QLabel("颜色模式:"))
        color_layout.addWidget(self.color_mode_combo)
        
        # 背景颜色
        self.bg_color_combo = QComboBox()
        self.bg_color_combo.addItems(["白色", "黑色", "透明"])
        color_layout.addWidget(QLabel("背景颜色:"))
        color_layout.addWidget(self.bg_color_combo)
        
        control_layout.addWidget(color_group)
        
        # 操作按钮组
        action_group = QGroupBox("操作")
        action_layout = QVBoxLayout(action_group)
        
        self.generate_btn = QPushButton("生成词云")
        self.save_btn = QPushButton("保存词云")
        self.preview_btn = QPushButton("实时预览")
        
        action_layout.addWidget(self.generate_btn)
        action_layout.addWidget(self.save_btn)
        action_layout.addWidget(self.preview_btn)
        
        control_layout.addWidget(action_group)
        
        # 添加弹性空间
        control_layout.addStretch()
        
        return control_widget
        
    def create_preview_panel(self):
        """创建预览面板"""
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        
        # 预览标题
        title_label = QLabel("词云预览")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        preview_layout.addWidget(title_label)
        
        # 词云画布
        self.canvas = WordCloudCanvas(self, width=10, height=8, dpi=100)
        preview_layout.addWidget(self.canvas)
        
        return preview_widget
        
    def init_data(self):
        """初始化数据"""
        self.mask_image = None
        self.color_image = None
        self.wordcloud = None
        self.preview_timer = QTimer()
        self.preview_timer.setInterval(500)  # 500ms延迟
        self.preview_timer.setSingleShot(True)
        
        # 设置默认路径
        self.setup_default_paths()
        
    def setup_default_paths(self):
        """设置默认路径"""
        system = platform.system()
        if system == "Windows":
            self.default_path = r"C:\Users\xushe\OneDrive\NAS云同步\Drive\社会工作\2025年07月05日短视频竞赛"
            self.font_path = r"C:\Windows\Fonts\simhei.ttf"
        elif system == "Darwin":  # macOS
            self.default_path = r"/Users/shengyixu/Library/CloudStorage/OneDrive-Personal/NAS云同步/Drive/社会工作/2025年07月05日短视频竞赛"
            self.font_path = r"/System/Library/Fonts/STHeiti Medium.ttc"
        else:  # Linux
            self.default_path = r"/home/xushe/OneDrive/NAS云同步/Drive/社会工作/2025年07月05日短视频竞赛"
            self.font_path = r"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            
    def setup_connections(self):
        """设置信号连接"""
        # 主题切换
        self.theme_btn.toggled.connect(self.toggle_theme)
        
        # 文件选择按钮
        self.freq_btn.clicked.connect(self.select_frequency_file)
        self.mask_btn.clicked.connect(self.select_mask_file)
        self.color_btn.clicked.connect(self.select_color_file)
        
        # 参数变化连接
        self.max_words_spin.valueChanged.connect(self.on_parameter_changed)
        self.max_font_spin.valueChanged.connect(self.on_parameter_changed)
        self.min_font_spin.valueChanged.connect(self.on_parameter_changed)
        self.relative_scaling_slider.valueChanged.connect(self.on_relative_scaling_changed)
        self.horizontal_slider.valueChanged.connect(self.on_horizontal_changed)
        self.margin_spin.valueChanged.connect(self.on_parameter_changed)
        
        # 颜色模式变化
        self.color_mode_combo.currentTextChanged.connect(self.on_color_mode_changed)
        self.bg_color_combo.currentTextChanged.connect(self.on_parameter_changed)
        
        # 操作按钮
        self.generate_btn.clicked.connect(self.generate_wordcloud)
        self.save_btn.clicked.connect(self.save_wordcloud)
        self.preview_btn.clicked.connect(self.toggle_preview)
        
        # 预览定时器
        self.preview_timer.timeout.connect(self.update_preview)
        
    def toggle_theme(self, checked):
        """切换主题"""
        self.dark_mode = checked
        self.apply_theme()
        
    def apply_theme(self):
        """应用主题样式"""
        if self.dark_mode:
            # 黑夜模式样式
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #555555;
                    border-radius: 5px;
                    margin-top: 1ex;
                    padding-top: 10px;
                    background-color: #3b3b3b;
                    color: #ffffff;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #ffffff;
                }
                QSlider::groove:horizontal {
                    border: 1px solid #666666;
                    height: 8px;
                    background: #444444;
                    margin: 2px 0;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #4a90e2;
                    border: 1px solid #5c6ac4;
                    width: 18px;
                    margin: -2px 0;
                    border-radius: 9px;
                }
                QPushButton {
                    background-color: #4a90e2;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #357abd;
                }
                QPushButton:pressed {
                    background-color: #2d5986;
                }
                QPushButton:checked {
                    background-color: #e74c3c;
                }
                QSpinBox, QComboBox {
                    background-color: #444444;
                    color: #ffffff;
                    border: 1px solid #666666;
                    border-radius: 3px;
                    padding: 2px;
                }
                QLabel {
                    color: #ffffff;
                }
                QSplitter::handle {
                    background-color: #555555;
                }
            """)
            self.theme_btn.setText("☀️ 白天模式")
        else:
            # 白天模式样式
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QWidget {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #cccccc;
                    border-radius: 5px;
                    margin-top: 1ex;
                    padding-top: 10px;
                    background-color: #ffffff;
                    color: #000000;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #000000;
                }
                QSlider::groove:horizontal {
                    border: 1px solid #999999;
                    height: 8px;
                    background: #ffffff;
                    margin: 2px 0;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #4a90e2;
                    border: 1px solid #5c6ac4;
                    width: 18px;
                    margin: -2px 0;
                    border-radius: 9px;
                }
                QPushButton {
                    background-color: #4a90e2;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #357abd;
                }
                QPushButton:pressed {
                    background-color: #2d5986;
                }
                QPushButton:checked {
                    background-color: #e74c3c;
                }
                QSpinBox, QComboBox {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    padding: 2px;
                }
                QLabel {
                    color: #000000;
                }
                QSplitter::handle {
                    background-color: #cccccc;
                }
            """)
            self.theme_btn.setText("🌙 黑夜模式")
        
    def select_frequency_file(self):
        """选择词频文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择词频文件", self.default_path, 
            "JSON文件 (*.json);;文本文件 (*.txt);;所有文件 (*)"
        )
        if file_path:
            try:
                if file_path.endswith('.json'):
                    # 加载JSON格式的词频文件
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.current_word_frequencies = json.load(f)
                else:
                    # 加载文本格式的词频文件
                    word_freq = {}
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and '\t' in line:
                                word, freq = line.split('\t', 1)
                                try:
                                    word_freq[word] = int(freq)
                                except ValueError:
                                    word_freq[word] = 1
                            elif line:
                                word_freq[line] = 1
                    self.current_word_frequencies = word_freq
                
                # 记录文件路径
                self.current_freq_file_path = file_path
                self.freq_label.setText(os.path.basename(file_path))
                self.on_parameter_changed()
                QMessageBox.information(self, "成功", f"已加载词频文件: {os.path.basename(file_path)}\n包含 {len(self.current_word_frequencies)} 个词汇")
                
            except Exception as e:
                QMessageBox.warning(self, "错误", f"无法加载词频文件: {str(e)}")
                
    def select_mask_file(self):
        """选择遮罩文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择遮罩图片", self.default_path, 
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            try:
                self.mask_image = np.array(Image.open(file_path))
                # 记录文件路径
                self.mask_file_path = file_path
                self.mask_label.setText(os.path.basename(file_path))
                self.on_parameter_changed()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"无法加载图片: {str(e)}")
                
    def select_color_file(self):
        """选择颜色文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择颜色图片", self.default_path, 
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            try:
                self.color_image = np.array(Image.open(file_path))
                # 记录文件路径
                self.color_file_path = file_path
                self.color_label.setText(os.path.basename(file_path))
                self.on_parameter_changed()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"无法加载图片: {str(e)}")
                
    def on_parameter_changed(self):
        """参数变化处理"""
        if self.preview_btn.text() == "停止预览":
            self.preview_timer.start()
            
    def on_relative_scaling_changed(self, value):
        """相对缩放变化"""
        scaling = value / 100.0
        self.relative_scaling_label.setText(f"{scaling:.1f}")
        self.on_parameter_changed()
        
    def on_horizontal_changed(self, value):
        """水平偏好变化"""
        horizontal = value / 100.0
        self.horizontal_label.setText(f"{horizontal:.1f}")
        self.on_parameter_changed()
        
    def on_color_mode_changed(self):
        """颜色模式变化"""
        self.on_parameter_changed()
        
    def generate_wordcloud(self):
        """生成词云"""
        try:
            # 获取参数
            max_words = self.max_words_spin.value()
            max_font_size = self.max_font_spin.value()
            min_font_size = self.min_font_spin.value()
            relative_scaling = self.relative_scaling_slider.value() / 100.0
            prefer_horizontal = self.horizontal_slider.value() / 100.0
            margin = self.margin_spin.value()
            
            # 背景颜色
            bg_color_map = {"白色": "white", "黑色": "black", "透明": None}
            background_color = bg_color_map[self.bg_color_combo.currentText()]
            
            # 创建词云
            wc = WordCloud(
                max_words=max_words,
                mask=self.mask_image,
                max_font_size=max_font_size,
                min_font_size=min_font_size,
                relative_scaling=relative_scaling,
                prefer_horizontal=prefer_horizontal,
                margin=margin,
                background_color=background_color,
                font_path=self.font_path,
                random_state=42
            )
            
            # 生成词云
            wc.generate_from_frequencies(self.current_word_frequencies)
            
            # 应用颜色
            color_mode = self.color_mode_combo.currentText()
            if color_mode == "灰度":
                wc = self.apply_grey_colors(wc)
            elif color_mode == "图片颜色" and self.color_image is not None:
                wc = self.apply_image_colors(wc)
                
            self.wordcloud = wc
            self.update_preview()
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"生成词云失败: {str(e)}")
            
    def apply_grey_colors(self, wc):
        """应用灰度颜色"""
        import random
        def grey_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
            return "hsl(0, 0%%, %d%%)" % random.randint(1, 20)
        return wc.recolor(color_func=grey_color_func, random_state=3)
        
    def apply_image_colors(self, wc):
        """应用图片颜色"""
        image_colors = ImageColorGenerator(self.color_image)
        return wc.recolor(color_func=image_colors)
        
    def update_preview(self):
        """更新预览"""
        if self.wordcloud is not None:
            color_mode = self.color_mode_combo.currentText()
            title = f"词云预览 - {color_mode}"
            self.canvas.update_wordcloud(self.wordcloud, title)
            
    def save_wordcloud(self):
        """保存词云"""
        if self.wordcloud is None:
            QMessageBox.warning(self, "警告", "请先生成词云")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存词云", self.default_path, 
            "PNG文件 (*.png);;JPG文件 (*.jpg);;所有文件 (*)"
        )
        if file_path:
            try:
                # 保存词云图片
                self.wordcloud.to_file(file_path)
                
                # 保存生成参数配置文件
                config_path = self.save_generation_config(file_path)
                
                QMessageBox.information(self, "成功", 
                    f"词云已保存到: {file_path}\n"
                    f"配置文件已保存到: {config_path}")
                    
            except Exception as e:
                QMessageBox.warning(self, "错误", f"保存失败: {str(e)}")
                
    def save_generation_config(self, image_path):
        """保存生成参数配置文件"""
        try:
            # 获取当前时间
            import datetime
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 收集所有生成参数
            config = {
                "生成时间": current_time,
                "词云图片路径": image_path,
                "词频文件": {
                    "路径": getattr(self, 'current_freq_file_path', "默认词频"),
                    "词汇数量": len(self.current_word_frequencies)
                },
                "遮罩图片": {
                    "路径": getattr(self, 'mask_file_path', "未选择"),
                    "尺寸": self.mask_image.shape if self.mask_image is not None else None
                },
                "颜色图片": {
                    "路径": getattr(self, 'color_file_path', "未选择"),
                    "尺寸": self.color_image.shape if self.color_image is not None else None
                },
                "词云参数": {
                    "最大词数": self.max_words_spin.value(),
                    "最大字体大小": self.max_font_spin.value(),
                    "最小字体大小": self.min_font_spin.value(),
                    "相对缩放": self.relative_scaling_slider.value() / 100.0,
                    "水平偏好": self.horizontal_slider.value() / 100.0,
                    "边距": self.margin_spin.value(),
                    "背景颜色": self.bg_color_combo.currentText(),
                    "颜色模式": self.color_mode_combo.currentText(),
                    "字体路径": self.font_path
                },
                "系统信息": {
                    "操作系统": platform.system(),
                    "Python版本": platform.python_version(),
                    "WordCloud版本": self.get_wordcloud_version()
                },
                "词频统计": {
                    "总词汇数": len(self.current_word_frequencies),
                    "最高频率": max(self.current_word_frequencies.values()) if self.current_word_frequencies else 0,
                    "最低频率": min(self.current_word_frequencies.values()) if self.current_word_frequencies else 0,
                    "平均频率": sum(self.current_word_frequencies.values()) / len(self.current_word_frequencies) if self.current_word_frequencies else 0
                }
            }
            
            # 生成配置文件路径（与图片同目录，同名但扩展名为.json）
            config_path = os.path.splitext(image_path)[0] + "_config.json"
            
            # 保存配置文件
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
            return config_path
            
        except Exception as e:
            print(f"保存配置文件失败: {str(e)}")
            return None
            
    def get_wordcloud_version(self):
        """获取WordCloud版本"""
        try:
            import wordcloud
            return wordcloud.__version__
        except:
            return "未知版本"
                
    def toggle_preview(self):
        """切换预览模式"""
        if self.preview_btn.text() == "实时预览":
            self.preview_btn.setText("停止预览")
            self.preview_btn.setStyleSheet("background-color: #e74c3c;")
        else:
            self.preview_btn.setText("实时预览")
            self.preview_btn.setStyleSheet("")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置高分屏支持
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 创建主窗口
    window = WordCloudGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 