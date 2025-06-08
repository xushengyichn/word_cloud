# - * - coding: utf - 8 -*-
"""
create wordcloud with chinese
=============================

Wordcloud is a very good tool, but if you want to create
Chinese wordcloud only wordcloud is not enough. The file
shows how to use wordcloud with Chinese. First, you need a
Chinese word segmentation library jieba, jieba is now the
most elegant the most popular Chinese word segmentation tool in python.
You can use 'PIP install jieba'. To install it. As you can see,
at the same time using wordcloud with jieba very convenient
"""

import jieba
# jieba.enable_parallel(4)
# Setting up parallel processes :4 ,but unable to run on Windows
from os import path
from imageio import imread
import matplotlib.pyplot as plt
import os
# jieba.load_userdict("txt\userdict.txt")
# add userdict by load_userdict()
from wordcloud import WordCloud, ImageColorGenerator

# get data directory (using getcwd() is needed to support running example in generated IPython notebook)
d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()

stopwords_path = os.path.join(d, "wc_cn/stopwords_cn_en.txt")
# Chinese fonts must be set
font_path = os.path.join(d, "fonts/SourceHanSerif/SourceHanSerifK-Light.otf")

# the path to save worldcloud
imgname1 = d + '/wc_cn/LuXun.jpg'
imgname2 = d + '/wc_cn/LuXun_colored.jpg'
# read the mask / color image taken from
back_coloring = imread(path.join(d, d + '/wc_cn/LuXun_color.jpg'))

text_path = os.path.join(d, "wc_cn/CalltoArms.txt")
userdict_list = ['阿Ｑ', '孔乙己', '单四嫂子']
text = open(text_path, encoding="utf-8").read()

def jieba_processing_txt(text, stopwords_path=None, userdict_list=None):
    if userdict_list:
        for word in userdict_list:
            jieba.add_word(word)

    seg_list = jieba.cut(text, cut_all=False)
    words = [w.strip() for w in seg_list if len(w.strip()) > 1]

    if stopwords_path:
        with open(stopwords_path, encoding='utf-8') as f:
            stopwords = set(f.read().splitlines())
        words = [w for w in words if w not in stopwords]

    return ' '.join(words)

processed_text = jieba_processing_txt(text, stopwords_path=stopwords_path, userdict_list=userdict_list)

wc = WordCloud(
    font_path=font_path,
    max_words=5000,
    mask=back_coloring,
    max_font_size=50,
    min_font_size=2,
    font_step=1,
    scale=2,
    prefer_horizontal=1.0,
    relative_scaling=0,
    random_state=42,
    background_color="white"
)
wc.generate(processed_text)

if __name__ == '__main__':
    image_colors_default = ImageColorGenerator(back_coloring)

    plt.figure()
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.show()

    wc.to_file(path.join(d, imgname1))

    image_colors_byImg = ImageColorGenerator(back_coloring)

    plt.imshow(wc.recolor(color_func=image_colors_byImg), interpolation="bilinear")
    plt.axis("off")
    plt.figure()
    plt.imshow(back_coloring, interpolation="bilinear")
    plt.axis("off")
    plt.show()

    wc.to_file(path.join(d, imgname2))
