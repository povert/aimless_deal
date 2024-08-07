# -*- coding: utf-8 -*-
import re
import pandas
import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import messagebox

STATE_NONE = 0
STATE_SELECT = 1
STATE_LOAD = 2
STATE_SHOW = 3
STATE_FINISH = 4

HEPL_TIP = '''1.请正确配置相应参数
2.支持正则筛序和替换
3.筛选字符为空则代表不筛选'''

ROW_MAX = 100       # 最大显示行数（对界面显示速度影响较大）


class ReplaceComponent(object):
    def __init__(self):
        self.state = STATE_NONE
        self.window = None              # 因为要监听窗口尺寸变化，所以引用一下窗口
        self.window_bind_id = 0
        self.frame = None
        self.diff_frame = None
        self.bottom_frame = None
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
        custom_font = font.Font(family='Arial', size=32)
        self.Lable_tip = tk.Label(self.frame, text=HEPL_TIP, justify=tk.CENTER, fg='grey', font=custom_font)
        self.Lable_tip.pack(fill=tk.BOTH, expand=True)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.inner_frame_update = False
        self.scrollable_canvas = None
        self.window = window
        self.window_bind_id = window.bind("<Configure>", self.on_resize)

    def hide(self):
        self.window.unbind("<Configure>", self.window_bind_id)
        self.inner_frame_update = False
        if self.frame:
            self.frame.pack_forget()

    def init_config_show(self):
        self.config_frame = ttk.Frame(self.frame)
        self.sheet_name_label = ttk.Combobox(self.config_frame, state='readonly')
        self.sheet_name_label['values'] = self.workspace.sheetnames
        self.sheet_name_label.current(0)
        self.sheet_name_label.grid(row=0, column=0, sticky=tk.EW, padx=5, pady=5)

        self.col_name_label = tk.Entry(self.config_frame, width=3)
        self.col_name_label.insert(0, 'A')
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
        self.replace_label.grid(row=0, column=6, sticky=tk.EW, padx=5, pady=5)

        self.replace_button = tk.Button(self.config_frame, text="替换", command=self.start_replace)
        self.replace_button.grid(row=0, column=7, sticky=tk.EW, padx=5, pady=5)

        for i in range(8):
            if i in (1, 2, 5, 7):     #1，2，5, 7组件宽度固定
                continue
            self.config_frame.columnconfigure(i, weight=1)

        self.config_frame.pack(fill=tk.X, expand=False, pady=(0, 0))

    def init_bottom_show(self):
        if self.bottom_frame:
            return
        self.bottom_frame = tk.Frame(self.frame)
        self.bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 0))
        self.fouse_button = tk.Button(self.bottom_frame, text="定位序号", command=self.fouse_text)
        self.fouse_button.grid(row=0, column=0, sticky=tk.EW, padx=(10, 0), pady=5)
        self.fouse_label = tk.Entry(self.bottom_frame, width=10)
        self.fouse_label.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        self.diff_button = tk.Button(self.bottom_frame, text="仅显示差异", command=self.show_diff)
        self.diff_button.grid(row=0, column=2, sticky=tk.EW, padx=(100, 5), pady=5)
        self.nodiff_button = tk.Button(self.bottom_frame, text="仅显示相同", command=self.show_nodiff)
        self.nodiff_button.grid(row=0, column=3, sticky=tk.EW, padx=5, pady=5)
        self.all_button = tk.Button(self.bottom_frame, text="显示全部", command=self.show_all)
        self.all_button.grid(row=0, column=4, sticky=tk.EW, padx=(5, 100), pady=5)
        self.shaixuan_button = tk.Button(self.bottom_frame, text="筛选", command=self.shaixuan)
        self.shaixuan_button.grid(row=0, column=5, sticky=tk.EW, padx=5, pady=5)
        self.last_page_button = tk.Button(self.bottom_frame, text="上一页", command=self.last_page)
        self.last_page_button.grid(row=0, column=6, sticky=tk.EW, padx=5, pady=5)
        self.page_text = tk.StringVar()
        self.page_text.set(f"{self.page}/{self.total_page}")
        self.page_label = tk.Label(self.bottom_frame, textvariable=self.page_text)
        self.page_label.grid(row=0, column=7, sticky=tk.EW, padx=5, pady=5)
        self.next_page_button = tk.Button(self.bottom_frame, text="下一页", command=self.next_page)
        self.next_page_button.grid(row=0, column=8, sticky=tk.EW, padx=5, pady=5)
        self.save_button = tk.Button(self.bottom_frame, text="保存结果", command=self.save_replace)
        self.save_button.grid(row=0, column=9, sticky=tk.EW, padx=5, pady=5)
        for i in range(10):
            if i in (1, 7,):
                continue
            self.bottom_frame.columnconfigure(i, weight=1)


    def start_replace(self):
        if not self.valid_replace():
            return
        self.release_diff_frame()
        self.Lable_tip.pack_forget()
        self.diff_frame = tk.Frame(self.frame)
        self.diff_frame.pack(fill=tk.BOTH, expand=True)
        v_scrollbar = tk.Scrollbar(self.diff_frame)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        scrollable_canvas = tk.Canvas(self.diff_frame, yscrollcommand=v_scrollbar.set)
        scrollable_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.config(command=scrollable_canvas.yview)
        self.inner_frame = tk.Frame(scrollable_canvas)
        scrollable_canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.inner_frame.bind("<Configure>", lambda event: scrollable_canvas.configure(scrollregion=scrollable_canvas.bbox("all")))
        # 某些平台不支持MouseWheel事件，需要使用Button-4和Button-5
        # scrollable_canvas.bind_all("<MouseWheel>", lambda event: scrollable_canvas.yview_scroll(int(-1 * event.delta / 120), "units"))
        scrollable_canvas.bind_all("<Button-4>", lambda e: scrollable_canvas.yview_scroll(-1, "units"))
        scrollable_canvas.bind_all("<Button-5>", lambda e: scrollable_canvas.yview_scroll(1, "units"))
        self.scrollable_canvas = scrollable_canvas
        for col in range(3):
            if col == 0:
                self.inner_frame.columnconfigure(col, weight=0)
            else:
                self.inner_frame.columnconfigure(col, weight=1)
        sheet_name = self.sheet_name_label.get()
        col_name = self.col_name_label.get()
        regx = self.regx_filter_label.get()
        col_work = self.workspace[sheet_name][col_name]
        self.diff_obj_list = []
        self.replace_series = pandas.Series()      # 使用pandas.Series存储替换结果
        if regx == "":
            self.show_cell_list = list(range(1, len(col_work)))
        else:
            self.show_cell_list = [i for i, cell in enumerate(col_work) if i!= 0 and re.search(regx, cell.value)]
        sumcount = len(self.show_cell_list) - 1  # 排除第一列，第一列为列名
        self.page = 1
        self.total_page = sumcount // ROW_MAX if sumcount % ROW_MAX == 0 else sumcount // ROW_MAX + 1
        self.init_bottom_show()
        self.show_page(1)


    def valid_replace(self):
        if self.sheet_name_label.get() not in self.workspace:
            messagebox.showinfo("提示","请输入正确的sheet工作表名")
            return False
        if not re.search('^[A-Z]+$', self.col_name_label.get()):
            messagebox.showinfo("提示","请输入正确的列名")
            return False
        if not self.repl_label.get():
            messagebox.showinfo("提示","请输入替换内容")
            return False
        return True

    def fouse_text(self):
        pass

    def show_diff(self):
        pass

    def show_nodiff(self):
        pass

    def show_all(self):
        pass

    def shaixuan(self):
        pass

    def last_page(self):
        self.show_page(self.page - 1)

    def next_page(self):
        self.show_page(self.page+1)

    def show_page(self, page):
        if self.page == 1:
            self.last_page_button.config(state=tk.NORMAL)
        if self.page == self.total_page:
            self.next_page_button.config(state=tk.NORMAL)
        self.page = page
        start_index = (page - 1) * ROW_MAX
        repr = self.repl_label.get()
        replace = self.replace_label.get()
        col_work = self.workspace[self.sheet_name_label.get()][self.col_name_label.get()]
        for i in range(start_index, start_index + ROW_MAX):
            if i < len(self.show_cell_list):
                index = self.show_cell_list[i]
                s1 = str(col_work[index].value)
                if not index in self.replace_series:
                    self.replace_series[index] = re.sub(repr, replace, s1)
                s2 = self.replace_series[index]
                if i - start_index == len(self.diff_obj_list):
                    self.diff_obj_list.append(CDiffRow(self.inner_frame, i - start_index))
                self.diff_obj_list[i - start_index].set_row(index, s1, s2)
                self.diff_obj_list[i - start_index].show()
            else:
                if i - start_index < len(self.diff_obj_list):
                    self.diff_obj_list[i - start_index].hide()
        if self.page == 1:
            self.last_page_button.config(state=tk.DISABLED)
        if self.page == self.total_page:
            self.next_page_button.config(state=tk.DISABLED)

    def save_replace(self):
        pass

    def on_resize(self, event):
        if self.scrollable_canvas and not self.inner_frame_update:
            self.inner_frame_update = True
            self.window.after(500, self.update_inner_frame)
    
    def update_inner_frame(self):
        if self.scrollable_canvas and self.inner_frame_update:
            self.scrollable_canvas.itemconfig(self.scrollable_canvas.find_withtag("all"), width=self.scrollable_canvas.winfo_width())
            # 更新内部框架的大小
            self.inner_frame.update_idletasks()  # 确保内部框架的大小得到更新
            self.inner_frame_update = False

    def release_diff_frame(self):
        if not self.diff_frame:
            return
        self.diff_frame.pack_forget()
        for widget in self.diff_frame.winfo_children():
            widget.destroy()
        self.diff_frame.destroy()
        self.diff_frame = None



class CDiffRow(object):
    def __init__(self, frame, row):
        self.index = 0
        self.state = False
        self.row = row
        self.label_text = tk.StringVar()
        self.lable = tk.Label(frame, textvariable=self.label_text, width=5, relief=tk.RIDGE)
        self.text1 = tk.Text(frame, height=1, state=tk.DISABLED)
        self.text2 = tk.Text(frame, height=1)

    def set_row(self, i, s1, s2):
        self.index = i
        self.label_text.set(str(i))
        self.text1.config(state=tk.NORMAL)
        self.text1.delete('1.0', tk.END)
        self.text1.insert(tk.END, s1)
        height1 = len(re.findall('\n', s1)) + 1
        self.text1.config(height=height1)
        self.text1.config(state=tk.DISABLED)
        self.text2.delete('1.0', tk.END)
        self.text2.insert(tk.END, s2)
        height2 = len(re.findall('\n', s2)) + 1
        self.text2.config(height=height2)

    def show(self):
        if self.state:
            return
        self.state = True
        self.lable.grid(row=self.row, column=0, sticky="nsew")
        self.text1.grid(row=self.row, column=1, sticky="nsew")
        self.text2.grid(row=self.row, column=2, sticky="nsew")

    def hide(self):
        if not self.state:
            return
        self.state = False
        self.lable.grid_forget()
        self.text1.grid_forget()
        self.text2.grid_forget()