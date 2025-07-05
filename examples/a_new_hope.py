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
    return "hsl(0, 0%%, %d%%)" % random.randint(20, 60)


# get data directory (using getcwd() is needed to support running example in generated IPython notebook)
d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()

# read the mask image taken from
# http://www.stencilry.org/stencils/movies/star%20wars/storm-trooper.gif
mask = np.array(Image.open("/Users/shengyixu/Library/CloudStorage/OneDrive-Personal/NAS云同步/Drive/社会工作/2025年07月05日短视频竞赛/金汇社区卫生服务中心2.png"))

# movie script of "a new hope"
# http://www.imsdb.com/scripts/Star-Wars-A-New-Hope.html
# May the lawyers deem this fair use.
text = open(path.join(d, 'a_new_hope.txt')).read()

# pre-processing the text a little bit
text = text.replace("HAN", "Han")
text = text.replace("LUKE'S", "Luke")

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
    # max_font_size=100,         # 减小最大字体大小
    # min_font_size=10          # 设置最小字体大小
    # relative_scaling=0.5,     # 增加相对缩放，让词频差异更明显
    # width=800,                # 设置宽度
    # height=600,               # 设置高度
    # prefer_horizontal=0.7     # 70%的词水平排列，30%垂直排列
)
wc.generate(text)

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
