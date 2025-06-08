import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

def boost_word_in_txt():
    # 选择文件
    filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if not filepath:
        return

    # 选择要增强的词
    word = simpledialog.askstring("关键词", "请输入要放大的词：")
    if not word:
        return

    # 设置增强次数
    try:
        repeat = int(simpledialog.askstring("次数", f"要增加“{word}”多少次？（建议 50~200）"))
    except (TypeError, ValueError):
        messagebox.showerror("错误", "次数无效")
        return

    # 读取文本
    with open(filepath, encoding='utf-8') as f:
        content = f.read()

    # 增强词频
    boosted = (" " + word) * repeat
    content += boosted

    # 弹窗显示结果
    preview = content[-1000:]  # 仅显示末尾部分预览
    messagebox.showinfo("修改预览（末尾部分）", preview)

    # 保存结果（覆盖原文件）
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    messagebox.showinfo("完成", f"已将“{word}”增加 {repeat} 次并写入文件。")

# 创建窗口
root = tk.Tk()
root.withdraw()  # 不显示主窗口
boost_word_in_txt()