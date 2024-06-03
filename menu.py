# -*- coding: utf-8 -*-
from tkinter import ttk
from tkinter import messagebox
import os
import tkinter as tk
import importlib
import pandas

class CMenu(object):
    def __init__(self, master):
        self.master = master
        self.model = None
        self.df = pandas.read_csv("./aaa.csv", header=None, names=["Question", "Ansewr"])


        master.geometry("400x800")
        master.title("SFT模型格式化输出")

        noun_frame = tk.Frame(master)
        noun_frame.pack(pady=10)
        noun_label = tk.Label(noun_frame, text="语料短语:")
        noun_label.pack(side=tk.LEFT)
        self.noun_entry = tk.Entry(noun_frame)
        self.noun_entry.pack(side=tk.LEFT, padx=(10, 0))

        model_frame = tk.Frame(master)
        model_frame.pack(pady=10)
        var = tk.StringVar()
        model_label = tk.Label(model_frame, text="语料模型:")
        model_label.pack(side=tk.LEFT)
        self.model_combobox = ttk.Combobox(model_frame, textvariable=var)
        self.model_combobox ['values'] = get_all_model()
        self.model_combobox.pack(side=tk.LEFT, padx=(10, 0))

        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)
        apply_button = tk.Button(button_frame, text="应用", command=self.apply_model)
        apply_button.pack(padx=10,pady=10, side=tk.LEFT)
        generate_button = tk.Button(button_frame, text="生成", command=self.generate_data)
        generate_button.pack(padx=10, pady=10, side=tk.LEFT)

        result_frame = tk.Frame(master)
        result_frame.pack(pady=10)
        scrollbar = tk.Scrollbar(result_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.records_listbox = tk.Listbox(result_frame, yscrollcommand=scrollbar.set, width=200)
        self.records_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.records_listbox.yview)

        format_frame = tk.Frame(master)
        format_frame.pack()
        self.key_listbox = tk.Listbox(format_frame, width=20)
        self.key_listbox.pack(pady=10)
        self.key_listbox.bind('<<ListboxSelect>>', self.on_select)  # 绑定选中事件
        self.value_entry = tk.Entry(format_frame, width=40)
        self.value_entry.pack(pady=5)
        self.default_select_key = None
        update_button = tk.Button(format_frame, text="更新值", command=self.update_value)
        update_button.pack(pady=10)

    def apply_model(self):
        noun = self.noun_entry.get()
        model_name = self.model_combobox.get()
        if not noun or not model_name:
            return
        module = importlib.import_module("sfttmodel.model." + model_name)
        self.model = module.CModel(noun)
        self.model.format_noun()
        self.default_select_key = None
        self.show_result()
        self.show_dict()

    def show_result(self):
        if not self.model:
            return
        question = self.model.question
        answer = self.model.answer
        self.records_listbox.delete(0, tk.END)
        for line in question.split("\n"):
            self.records_listbox.insert(tk.END, line)
        self.records_listbox.insert(tk.END, "")
        for line in answer.split("\n"):
            self.records_listbox.insert(tk.END, line)
    def show_dict(self):
        if not self.model:
            return
        my_dict = self.model.get_format_data()
        self.key_listbox.delete(0, tk.END)  # 清空列表框内容
        for key in my_dict:
            self.key_listbox.insert(tk.END, key)  # 插入键到列表框
    def on_select(self, event):
        if not self.model:
            return
        my_dict = self.model.get_format_data()
        selected_key = event.widget.curselection()
        if selected_key:
            selected_key = selected_key[0]  # 获取选中的索引
            current_key = event.widget.get(selected_key)  # 获取选中的键
            self.default_select_key = current_key
            self.value_entry.delete(0, tk.END)  # 清空输入框
            self.value_entry.insert(0, my_dict.get(current_key, ""))  # 插入对应的值

    def update_value(self):
        if not self.model:
            return
        selected_key = self.key_listbox.curselection()
        if selected_key:
            selected_key = selected_key[0]  # 获取选中的索引
            current_key = self.key_listbox.get(selected_key)  # 获取选中的键
        else:
            current_key = self.default_select_key
        if current_key:
            new_value = self.value_entry.get()  # 获取输入框中的新值
            if new_value:  # 确保新值不为空
                new_format = {current_key:new_value}
                my_dict = self.model.get_format_data()
                self.model.out_format(new_format)
                self.value_entry.delete(0, tk.END)  # 清空输入框
                self.value_entry.insert(0, my_dict.get(current_key, ""))  #插入更新后的值
                self.model.format_noun()
                self.default_select_key = None
                self.show_result()

    def generate_data(self):
        if not self.model:
            self.apply_model()
        if not self.model:
            return
        if not self.model.answer or self.model.question:
            self.model.format_noun()
        if len(self.df.loc[(self.df["Question"] == self.model.question) & (self.df["Ansewr"] == self.model.answer)]) != 0:
            messagebox.showinfo("添加数据失败", "该数据已存在")
            return
        self.df.loc[len(self.df)] = self.model.out_put()
        self.df.to_csv("./aaa.csv", index=False, header=False)
        messagebox.showinfo("添加数据成功", "添加数据成功")

current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)

def get_all_model():
    model_list = []
    for file_name in os.listdir(os.path.join(current_dir_path, "model")):
        if not file_name.endswith(".py"):
            continue
        if file_name in ("base.py", "__init__.py"):
            continue
        model_list.append(file_name[:-3])
    return model_list

if __name__ == "__main__":
    root = tk.Tk()
    CMenu(root)
    root.mainloop()