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

from wordcloud import WordCloud, STOPWORDS


def grey_color_func(word, font_size, position, orientation, random_state=None,
                    **kwargs):
    return "hsl(0, 0%%, %d%%)" % random.randint(1, 20)


# get data directory (using getcwd() is needed to support running example in generated IPython notebook)
d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()

# read the mask image taken from
# http://www.stencilry.org/stencils/movies/star%20wars/storm-trooper.gif
mask = np.array(Image.open("/Users/shengyixu/Library/CloudStorage/OneDrive-Personal/NAS云同步/Drive/社会工作/2025年07月05日短视频竞赛/中企联合大厦简笔画1.png"))

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

# wc = WordCloud(max_words=1000, mask=mask, stopwords=stopwords, margin=10,
            #    random_state=1, background_color='white').generate(text)

# store default colored image
default_colors = wc.to_array()
plt.title("Custom colors")
plt.imshow(wc.recolor(color_func=grey_color_func, random_state=3),
           interpolation="bilinear")
wc.to_file("a_new_hope.png")
plt.axis("off")
plt.figure()
plt.title("Default colors")
plt.imshow(default_colors, interpolation="bilinear")
plt.axis("off")
plt.show()
