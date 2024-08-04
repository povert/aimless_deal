# -*- coding: utf-8 -*-
import os
import pandas
import tkinter as tk
from tkinter import ttk

STATE_NONE = 0
STATE_SELECT = 1
STATE_LOAD = 2
STATE_SHOW = 3
STATE_FINISH = 4
class HomeComponent(object):
    def __init__(self):
        self.state = STATE_NONE
        self.frame = None
        self.workspace = None
        self.next_step = None

    def col(self, S):
        return ord(S) - ord('A')
    def set_workspace(self, workspace):
        self.workspace = workspace

    def show(self, window, next_step):
        self.next_step = next_step
        self.frame = tk.Frame(window)
        self.init_config_show()
        self.frame.pack(fill=tk.BOTH, expand=True)

    def init_config_show(self):
        self.config_frame = tk.Frame(self.frame)
        self.sheet_name_label = ttk.Combobox(self.config_frame, state='readonly')
        self.sheet_name_label['values'] = self.workspace.sheetnames
        self.sheet_name_label.current(0)
        self.sheet_name_label.grid(row=0, column=0, sticky=tk.EW, padx=5, pady=5)

        self.col_name_label = tk.Entry(self.config_frame, width=3)
        self.col_name_label.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)

        self.regx_filter_type = ttk.Combobox(self.config_frame, values=['包含', '不包含', '等于'], state='readonly', width=4)
        self.regx_filter_type.current(0)
        self.regx_filter_type.grid(row=0, column=2, sticky=tk.EW, padx=5, pady=5)

        self.regx_filter_label = tk.Entry(self.config_frame)
        self.regx_filter_label.grid(row=0, column=3, sticky=tk.EW, padx=5, pady=5)

        self.repl_label = tk.Entry(self.config_frame)
        self.repl_label.grid(row=0, column=4, sticky=tk.EW, padx=(30, 5), pady=5)

        label = tk.Label(self.config_frame, width=5, text="替换为:")
        label.grid(row=0, column=5, sticky=tk.EW)

        self.replace_label = tk.Entry(self.config_frame)
        self.replace_label.grid(row=0, column=6, sticky=tk.EW, padx=(5, 30), pady=5)

        for i in range(7):
            if i in (1, 2, 5):     #1，2，5组件宽度固定
                continue
            self.config_frame.columnconfigure(i, weight=1)

        self.config_frame.pack(fill=tk.BOTH, expand=True)




