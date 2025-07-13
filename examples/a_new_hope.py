#!/usr/bin/env python
"""
Using custom colors
===================

Using the recolor method and custom coloring functions.
"""

import numpy as np
from PIL import Image
from os import path
import matplotlib.pyplot as plt
import os
import random
import platform

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


def grey_color_func(word, font_size, position, orientation, random_state=None,
                    **kwargs):
    return "hsl(0, 0%%, %d%%)" % random.randint(1, 20)


# get data directory (using getcwd() is needed to support running example in generated IPython notebook)
d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()

# 根据操作系统自动选择路径和字体
def get_onedrive_path():
    system = platform.system()
    if system == "Windows":
        return r"C:\Users\xushe\OneDrive\NAS云同步\Drive\社会工作\2025年07月05日短视频竞赛"
    elif system == "Darwin":  # macOS
        return r"/Users/shengyixu/Library/CloudStorage/OneDrive-Personal/NAS云同步/Drive/社会工作/2025年07月05日短视频竞赛"
    else:  # Linux 或其他系统
        return r"/home/xushe/OneDrive/NAS云同步/Drive/社会工作/2025年07月05日短视频竞赛"

def get_font_path():
    system = platform.system()
    if system == "Windows":
        return r"C:\Windows\Fonts\simhei.ttf"  # Windows中文字体
    elif system == "Darwin":  # macOS
        return r"/System/Library/Fonts/STHeiti Medium.ttc"  # macOS中文字体
    else:  # Linux 或其他系统
        return r"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # Linux默认字体

# 获取OneDrive路径和字体路径
onedrive_path = get_onedrive_path()
font_path = get_font_path()

# 选择生成模式：'grey' 为灰度，'image' 为图片颜色，'both' 为两种都生成
GENERATION_MODE = 'grey'  # 可以改为 'image' 或 'both'

# 定义输入文件名
MASK_FILENAME = "中企联合大厦简笔画1.png"
COLOR_FILENAME = "中企联合大厦简笔画1.png"

# 定义输出文件名（自动提取输入文件名作为前缀）
def get_output_filename(prefix, suffix):
    # 从mask文件名提取基础名称（去掉扩展名）
    base_name = os.path.splitext(MASK_FILENAME)[0]
    return f"{base_name}_{prefix}.png"

# read the mask image taken from
# http://www.stencilry.org/stencils/movies/star%20wars/storm-trooper.gif
mask = np.array(Image.open(os.path.join(onedrive_path, MASK_FILENAME)))

# 读取颜色图片（可以是彩色版本的mask图片）
color_image = np.array(Image.open(os.path.join(onedrive_path, COLOR_FILENAME)))

# 导入词频数据
from word_frequencies import word_frequencies

# adding movie script specific stopwords
stopwords = set(STOPWORDS)
stopwords.add("int")
stopwords.add("ext")

wc = WordCloud(
    max_words=1000,           # 增加最大词数
    mask=mask, 
    stopwords=stopwords,
    margin=10,
    random_state=1,
    background_color='white',
    font_path=font_path,  # 自动选择系统中文字体
    max_font_size=30,         # 减小最大字体大小
    min_font_size=1,          # 设置最小字体大小
    # relative_scaling=0.1,     # 增加相对缩放，让词频差异更明显
    # width=800,                # 设置宽度
    # height=600,               # 设置高度
    # prefer_horizontal=0.7     # 70%的词水平排列，30%垂直排列
)
# 直接使用词频生成词云，而不是处理文本
wc.generate_from_frequencies(word_frequencies)

# 创建从图片中获取颜色的生成器
image_colors = ImageColorGenerator(color_image)

# store default colored image
default_colors = wc.to_array()
# 根据生成模式选择显示和保存
if GENERATION_MODE == 'grey':
    # 只生成灰度版本
    fig, axes = plt.subplots(1, 1, figsize=(8, 6))
    axes.set_title("Grey colors")
    axes.imshow(wc.recolor(color_func=grey_color_func, random_state=3),
               interpolation="bilinear")
    axes.axis("off")
    plt.tight_layout()
    plt.show()
    
    # 保存灰度版本
    grey_output = get_output_filename("grey", "png")
    wc.recolor(color_func=grey_color_func, random_state=3).to_file(os.path.join(onedrive_path, grey_output))
    
elif GENERATION_MODE == 'image':
    # 只生成图片颜色版本
    fig, axes = plt.subplots(1, 1, figsize=(8, 6))
    axes.set_title("Image colors")
    axes.imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
    axes.axis("off")
    plt.tight_layout()
    plt.show()
    
    # 保存图片颜色版本
    image_output = get_output_filename("image_colors", "png")
    wc.recolor(color_func=image_colors).to_file(os.path.join(onedrive_path, image_output))
    
elif GENERATION_MODE == 'both':
    # 生成所有版本（原来的代码）
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # 1. 默认颜色
    axes[0].set_title("Default colors")
    axes[0].imshow(default_colors, interpolation="bilinear")
    axes[0].axis("off")

    # 2. 灰度颜色
    axes[1].set_title("Grey colors")
    axes[1].imshow(wc.recolor(color_func=grey_color_func, random_state=3),
                   interpolation="bilinear")
    axes[1].axis("off")

    # 保存黑白的版本
    grey_output = get_output_filename("grey", "png")
    wc.recolor(color_func=grey_color_func, random_state=3).to_file(os.path.join(onedrive_path, grey_output))

    # 3. 从图片获取的颜色
    axes[2].set_title("Image colors")
    axes[2].imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
    axes[2].axis("off")

    plt.tight_layout()
    plt.show()

    # 保存图片颜色版本
    image_output = get_output_filename("image_colors", "png")
    wc.recolor(color_func=image_colors).to_file(os.path.join(onedrive_path, image_output))
