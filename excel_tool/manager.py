# -*- coding: utf-8 -*-
import tkinter as tk
import importlib

STATE_NONE = 0
STATE_LOAD_FILE = 1
STATE_SHOW_HOME = 2

class Manager(object):
    def __init__(self):
        self.window = tk.Tk()
        self.state = STATE_NONE
        self.init_window()
        self.component = None
        self.config_component = {
            "select" : "excel_tool.select.SelectFileComponent",
            "replace" : "excel_tool.replace.ReplaceComponent"
        }

    def init_window(self):
        # screen_width = self.window.winfo_screenwidth()
        # screen_height = self.window.winfo_screenheight()
        screen_width = 2560
        screen_height = 1440
        self.window_width = screen_width // 2
        self.window_height = screen_height // 2
        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2
        self.window.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

    def load_component(self, name):
        module_name, class_name = self.config_component[name].rsplit(".", 1)
        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)
        component = class_()
        return component

    def next_step(self, component):
        if self.state == STATE_LOAD_FILE and component == self.component:
            self.component.hide()
            workspace = self.component.work_space
            file_name = self.component.filename.get()
            self.component = self.load_component("replace")
            self.component.set_workspace(workspace, file_name)
            self.state = STATE_SHOW_HOME
            self.component.show(self.window, self.next_step)
        elif self.state == STATE_SHOW_HOME and component == self.component:
            self.component.hide()
            self.state = STATE_LOAD_FILE
            self.component = self.load_component("select")
            self.component.show(self.window, self.next_step)

    def run(self):
        self.state = STATE_LOAD_FILE
        self.component = self.load_component("select")
        import openpyxl
        # self.component = self.load_component("replace")
        # file = '/home/flyer/文档/povert/aimless_deal/codelf/dictdata/简明英汉词典（vivo_edited）.xlsx'
        # file = '/home/flyer/文档/povert/pandas_study/deal.xlsx'
        # work_space = openpyxl.open(file)
        # work_space = openpyxl.open('/home/flyer/文档/povert/pandas_study/38. batch_chinese_english.xlsx')
        # self.component.set_workspace(work_space, file)
        self.component.show(self.window, self.next_step)
        self.window.mainloop()




if __name__ == '__main__':
    manager = Manager()
    manager.run()