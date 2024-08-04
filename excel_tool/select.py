# -*- coding: utf-8 -*-
import os
import openpyxl
import threading
import traceback
import tkinter as tk
from tkinter import filedialog

STATE_NONE = 0
STATE_SHOW = 1
STATE_LOAD = 2
STATE_FINISH = 3
class SelectFileComponent(object):
    def __init__(self):
        self.state = STATE_NONE
        self.filename = tk.StringVar()
        self.work_space = None
        self.frame = None
        self.next_step = None

    def show(self, window, next_step):
        if self.state != STATE_NONE:
            return
        self.state = STATE_SHOW
        self.next_step = next_step
        self.frame = tk.Frame(window)
        self.select_button = tk.Button(self.frame, text="选择文件", command=self.OnButtonClick)
        self.select_button.pack(pady=10)
        self.select_text = tk.Entry(self.frame, textvariable=self.filename, width=80)
        self.filename.trace_add('write', self.on_filename_change)
        self.select_text.pack(pady=10)
        self.tip_txt = tk.StringVar()
        tip = tk.Label(self.frame, textvariable=self.tip_txt)
        tip.pack(pady=10)
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def hide(self):
        if self.frame:
            self.frame.place_forget()

    def OnButtonClick(self):
        button_txt = self.select_button.cget("text")
        if button_txt == '选择文件':
            self.select_file()
        else:
            self.Load_file()
    def select_file(self):
        filename = filedialog.askopenfilename(
            title="选择文件",
            filetypes=(("xlsx文件", "*.xlsx"),)
        )
        if not filename:
            return
        else:
            self.select_text.delete(0, tk.END)
            self.select_text.insert(0, filename)
            self.Load_file()

    def Load_file(self):
        filename = self.filename.get()
        filename = filename.strip()
        if not filename:
            self.tip_txt.set("输入的文件名为空")
            self.select_text.delete(0, tk.END)
            return
        if not filename.endswith('.xlsx'):
            self.tip_txt.set(f"输入的文件{filename}不是.xlsx文件")
            self.select_text.delete(0, tk.END)
            return
        if not os.path.exists(filename):
            self.tip_txt.set(f"输入的文件{filename}不存在")
            self.select_text.delete(0, tk.END)
            return
        if self.state == STATE_LOAD:
            self.tip_txt.set(f"文件{filename}正在加载中，请稍后。。。")
            self.select_text.delete(0, tk.END)
            return
        self.state = STATE_LOAD
        self.tip_txt.set(f"文件{filename}正在加载中，请稍后。。。")
        self.select_text.config(state=tk.DISABLED)
        self.select_button.config(state=tk.DISABLED)
        threading.Thread(target=self.true_load_file, args=(filename, self.load_over)).start()

    def true_load_file(self, filename, callback):
        try:
            self.work_space = openpyxl.load_workbook(filename)
        except:
            traceback.print_exc()
            callback(False)
            return
        callback(True)

    def load_over(self, ret):
        if ret:
            self.state = STATE_FINISH
            filename = self.filename.get()
            self.tip_txt.set(f"载入文件{filename}成功")
            if self.next_step:
                self.next_step(self)
        else:
            self.state = STATE_SHOW
            filename = self.filename.get()
            self.tip_txt.set(f"载入文件{filename}居然出错了，请重新选择文件")
            self.select_text.delete(0, tk.END)
            self.select_text.config(state=tk.DISABLED)
            self.select_button.config(state=tk.DISABLED)

    def on_filename_change(self, *args):
        filename = self.filename.get()
        filename = filename.strip()
        if filename != '' and self.select_button.cget("text") == "选择文件":
            self.select_button.config(text="加载文件")
        elif filename == '' and self.select_button.cget("text") == "加载文件":
            self.select_button.config(text="选择文件")

