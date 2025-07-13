#!/usr/bin/env python
"""
WordCloud 配置文件查看器
=======================
用于查看和加载之前保存的词云生成配置文件
"""

import sys
import os
import json
import platform
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QPushButton, QFileDialog, 
                             QLabel, QMessageBox, QSplitter, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap


class ConfigViewer(QMainWindow):
    """配置文件查看器主窗口"""
    
    def __init__(self):
        super().__init__()
        self.current_config = None
        self.init_ui()
        self.setup_default_paths()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("WordCloud 配置文件查看器")
        self.setGeometry(200, 200, 1000, 700)
        
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
        
        # 右侧显示区域
        display_panel = self.create_display_panel()
        splitter.addWidget(display_panel)
        
        # 设置分割器比例
        splitter.setSizes([300, 700])
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
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
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 10px;
            }
        """)
        
    def create_control_panel(self):
        """创建控制面板"""
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        
        # 文件操作组
        file_group = QGroupBox("文件操作")
        file_layout = QVBoxLayout(file_group)
        
        self.load_btn = QPushButton("加载配置文件")
        self.load_btn.clicked.connect(self.load_config_file)
        file_layout.addWidget(self.load_btn)
        
        self.load_from_image_btn = QPushButton("从图片加载配置")
        self.load_from_image_btn.clicked.connect(self.load_config_from_image)
        file_layout.addWidget(self.load_from_image_btn)
        
        self.export_btn = QPushButton("导出配置")
        self.export_btn.clicked.connect(self.export_config)
        self.export_btn.setEnabled(False)
        file_layout.addWidget(self.export_btn)
        
        control_layout.addWidget(file_group)
        
        # 配置信息组
        info_group = QGroupBox("配置信息")
        info_layout = QVBoxLayout(info_group)
        
        self.info_label = QLabel("未加载配置文件")
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        
        control_layout.addWidget(info_group)
        
        # 图片预览组
        preview_group = QGroupBox("词云预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_label = QLabel("无预览")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setStyleSheet("border: 1px solid #cccccc; background-color: #f9f9f9;")
        preview_layout.addWidget(self.preview_label)
        
        control_layout.addWidget(preview_group)
        
        # 添加弹性空间
        control_layout.addStretch()
        
        return control_widget
        
    def create_display_panel(self):
        """创建显示面板"""
        display_widget = QWidget()
        display_layout = QVBoxLayout(display_widget)
        
        # 标题
        title_label = QLabel("配置文件内容")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        display_layout.addWidget(title_label)
        
        # 配置内容显示
        self.config_text = QTextEdit()
        self.config_text.setReadOnly(True)
        display_layout.addWidget(self.config_text)
        
        return display_widget
        
    def setup_default_paths(self):
        """设置默认路径"""
        system = platform.system()
        if system == "Windows":
            self.default_path = r"C:\Users\xushe\OneDrive\NAS云同步\Drive\社会工作\2025年07月05日短视频竞赛"
        elif system == "Darwin":  # macOS
            self.default_path = r"/Users/shengyixu/Library/CloudStorage/OneDrive-Personal/NAS云同步/Drive/社会工作/2025年07月05日短视频竞赛"
        else:  # Linux
            self.default_path = r"/home/xushe/OneDrive/NAS云同步/Drive/社会工作/2025年07月05日短视频竞赛"
            
    def load_config_file(self):
        """加载配置文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择配置文件", self.default_path, 
            "JSON文件 (*.json);;所有文件 (*)"
        )
        if file_path:
            self.load_config(file_path)
            
    def load_config_from_image(self):
        """从图片文件加载对应的配置文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择词云图片", self.default_path, 
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            # 生成对应的配置文件路径
            config_path = os.path.splitext(file_path)[0] + "_config.json"
            if os.path.exists(config_path):
                self.load_config(config_path)
            else:
                QMessageBox.warning(self, "错误", f"未找到对应的配置文件: {config_path}")
                
    def load_config(self, config_path):
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.current_config = json.load(f)
                
            # 显示配置内容
            self.config_text.setText(json.dumps(self.current_config, ensure_ascii=False, indent=2))
            
            # 更新信息显示
            self.update_info_display()
            
            # 更新图片预览
            self.update_image_preview()
            
            # 启用导出按钮
            self.export_btn.setEnabled(True)
            
            QMessageBox.information(self, "成功", f"已加载配置文件: {os.path.basename(config_path)}")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法加载配置文件: {str(e)}")
            
    def update_info_display(self):
        """更新信息显示"""
        if not self.current_config:
            return
            
        info_text = f"""
生成时间: {self.current_config.get('生成时间', '未知')}
词云图片: {os.path.basename(self.current_config.get('词云图片路径', '未知'))}
词汇数量: {self.current_config.get('词频文件', {}).get('词汇数量', 0)}
遮罩图片: {os.path.basename(self.current_config.get('遮罩图片', {}).get('路径', '未选择'))}
颜色图片: {os.path.basename(self.current_config.get('颜色图片', {}).get('路径', '未选择'))}
        """.strip()
        
        self.info_label.setText(info_text)
        
    def update_image_preview(self):
        """更新图片预览"""
        if not self.current_config:
            return
            
        image_path = self.current_config.get('词云图片路径')
        if image_path and os.path.exists(image_path):
            try:
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    # 缩放图片以适应预览区域
                    scaled_pixmap = pixmap.scaled(
                        self.preview_label.width(), 
                        self.preview_label.height(),
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    self.preview_label.setPixmap(scaled_pixmap)
                    return
            except Exception as e:
                print(f"加载图片预览失败: {str(e)}")
                
        self.preview_label.setText("图片不可用")
        
    def export_config(self):
        """导出配置"""
        if not self.current_config:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出配置文件", self.default_path, 
            "JSON文件 (*.json);;所有文件 (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_config, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "成功", f"配置文件已导出到: {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"导出失败: {str(e)}")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置高分屏支持
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 创建主窗口
    window = ConfigViewer()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 