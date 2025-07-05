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

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


def grey_color_func(word, font_size, position, orientation, random_state=None,
                    **kwargs):
    return "hsl(0, 0%%, %d%%)" % random.randint(1, 20)


# get data directory (using getcwd() is needed to support running example in generated IPython notebook)
d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()

# read the mask image taken from
# http://www.stencilry.org/stencils/movies/star%20wars/storm-trooper.gif
mask = np.array(Image.open("/Users/shengyixu/Library/CloudStorage/OneDrive-Personal/NAS云同步/Drive/社会工作/2025年07月05日短视频竞赛/金汇社区卫生服务中心2.png"))

# 读取颜色图片（可以是彩色版本的mask图片）
color_image = np.array(Image.open("/Users/shengyixu/Library/CloudStorage/OneDrive-Personal/NAS云同步/Drive/社会工作/2025年07月05日短视频竞赛/金汇社区卫生服务中心3.png"))

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
    font_path='/System/Library/Fonts/STHeiti Medium.ttc',  # 使用系统中文字体
    max_font_size=50,         # 减小最大字体大小
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
# 显示三种不同的效果
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
wc.to_file("a_new_hope_black_white.png")

# 3. 从图片获取的颜色
axes[2].set_title("Image colors")
axes[2].imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
axes[2].axis("off")

plt.tight_layout()
plt.show()

# 保存两个版本
wc.recolor(color_func=image_colors).to_file("a_new_hope_image_colors.png")
