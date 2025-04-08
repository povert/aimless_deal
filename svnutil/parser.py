# -*- coding: utf-8 -*-
import subprocess
import re
import os
import logging

if os.environ.get("LANG") == "C.UTF-8":
    SVN_LASTVERSION_COMPILE = re.compile(r"Revision: (\d+)")
else:  # 中文环境变量下显示版本两个字
    SVN_LASTVERSION_COMPILE = re.compile(r"版本: (\d+)")
SVN_LOG_INFO_COMPILE = re.compile(r"^r(\d+) \S (\S+).*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*")
SVN_INDEX_FILE_COMPILE = re.compile(r"^Index:.(\S+)")
FILE_LASTVERSION = re.compile(r"^--- (\S+)\t\((.*)\)")
FILE_NOW_VERSION = re.compile(r"^\+\+\+ (\S+)\t\((.*)\)")
FILE_TOP = re.compile(r"^@@\s-(\d+),(\d+)\s\+(\d+),(\d+)\s@@")


def exec_svn_command(cmd):
    o_exec_result = subprocess.run(cmd, capture_output=True, shell=True)
    s_exec_out = o_exec_result.stdout.decode("utf-8")
    if s_exec_out:
        return 1, s_exec_out
    s_exec_err = o_exec_result.stderr.decode("utf-8")
    return 0, s_exec_err


def get_latest_version(url):
    cmd = "svn info %s" % url
    t_info = exec_svn_command(cmd)
    if not t_info[0]:
        logging.error("执行'%s'指令出错：%s" % (cmd, t_info[1]))
        return None
    s_info = t_info[1]
    lines = s_info.splitlines()
    o_match = SVN_LASTVERSION_COMPILE.match(lines[5])
    version = int(o_match.group(1))
    return version


def get_patch_by_version(url, start_version, end_version):
    cmd = "svn log %s --diff -r%d:%d" % (url, start_version, end_version)
    t_info = exec_svn_command(cmd)
    if not t_info[0]:
        logging.error("执行'%s'指令出错：%s" % (cmd, t_info[1]))
        return None
    s_info = t_info[1]
    o_parser_log = ParserLog()
    result_data = o_parser_log.start_deal(s_info)
    return result_data


class ParserLog(object):
    # 单例模式来保存和处理SVN日志
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ParserLog, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.patch_data = []
        self.parser_patch = Patch()

    def start_deal(self, s_info):
        # 按一行一行读取，指定步骤那样解析补丁
        self.parser(s_info)
        d_result = self.out_put_result(is_keep=False)
        return d_result

    def parser(self, s_info):
        # 按一行一行读取，指定步骤那样解析补丁
        step_index = 0
        current_patch = self.parser_patch
        current_patch.init()
        patch_file_data = {}
        lines = s_info.splitlines()
        for line in lines:
            if not line:
                continue
            if line == "------------------------------------------------------------------------":
                # 标志符，一次提交的结束，记录并结束上次补丁信息
                if step_index >= 3:
                    current_patch.is_done = 1
                    if not current_patch.next_patch:
                        current_patch.next_patch = Patch()
                    current_patch = current_patch.next_patch
                    current_patch.init()
                step_index = 1
            elif line.startswith("Index: "):
                # 标志符，补丁有一个新文件有变动
                step_index = 3
                file_name = SVN_INDEX_FILE_COMPILE.match(line).group(1)
                patch_file_data = {"file_name": file_name, "Op": "M", "patch": {"Add": [], "Del": [], "Equ": []}}
                if line.endswith("(deleted)"):
                    # 删除的文件直接加入补丁文件列表，方便处理删除
                    step_index = 99
                    patch_file_data["Op"] = "D"
                    current_patch.patch_file_data[file_name] = patch_file_data
            elif line == "===================================================================":
                # 标志符，一个文件补丁信息的开始处理（文件补丁结束处理是正确处理@@ -0,0 +1,2 @@字段后添加到current_patch.patch_file_data列表）
                step_index = 4
            elif step_index == 99:
                continue
            elif step_index == 1:
                step_index = 2
                match = SVN_LOG_INFO_COMPILE.match(line)
                current_patch.version = int(match.group(1))
                current_patch.author = match.group(2)
                current_patch.date = match.group(3)
            elif step_index == 2:
                if current_patch.message:
                    current_patch.message += "\n"
                current_patch.message += "%s" % line
            elif step_index in (4, 5):
                step_index += 1
                if step_index == 5:
                    match = FILE_LASTVERSION.match(line)
                    if not match:
                        step_index = 99
                    else:
                        file_name = match.group(1)
                        if file_name != patch_file_data["file_name"]:
                            logging.warning(
                                "版本%s文件名不匹配%s!=%s,忽略" % (
                                    current_patch.version, file_name, patch_file_data["file_name"]))
                        version = match.group(2)
                        if version == "不存在的":
                            patch_file_data["Op"] = "A"
                else:
                    match = FILE_NOW_VERSION.match(line)
                    if not match:
                        step_index = 99
                    else:
                        file_name = match.group(1)
                        if file_name != patch_file_data["file_name"]:
                            logging.warning(
                                "版本%s文件名不匹配%s!=%s,忽略" % (
                                    current_patch.version, file_name, patch_file_data["file_name"]))
            elif step_index == 6:
                # 一个文件会被改动多次，所以7结束后会重新设置成为6匹配下一个补丁
                step_index = 7
                match = FILE_TOP.match(line)
                if not match:
                    step_index = 99
                    continue
                patch_file_data["calculated_numbers"] = (
                    int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)))
            elif step_index == 7:
                if line == r"\ No newline at end of file":
                    continue
                operation = line[0]
                text = line[1:]
                start_old, end_old, start_new, end_new = patch_file_data["calculated_numbers"]
                add_list, delete_list, equal_list = patch_file_data["patch"]["Add"], patch_file_data["patch"]["Del"], \
                    patch_file_data["patch"]["Equ"]
                if operation == "-":
                    delete_list.append((start_old, text))
                    start_old += 1
                    end_old -= 1
                elif operation == "+":
                    add_list.append((start_new, text))
                    start_new += 1
                    end_new -= 1
                else:
                    equal_list.append((start_new, text))
                    start_old += 1
                    end_old -= 1
                    start_new += 1
                    end_new -= 1
                patch_file_data["calculated_numbers"] = (start_old, end_old, start_new, end_new)
                if end_new <= 0 and end_old <= 0:
                    step_index = 6
                    del patch_file_data["calculated_numbers"]
                    current_patch.patch_file_data[patch_file_data["file_name"]] = patch_file_data
                    if end_new != 0 or end_old != 0:
                        logging.warning("版本%s补丁文件%s内容解析结束不对,结束后参数(%s,%s,%s,%s)，已忽略该错误" %
                                        (current_patch.version, patch_file_data["file_name"], start_old, end_old,
                                         start_new, end_new))

    def out_put_result(self, keep_num=10, is_keep=True):
        d_result = {}
        o_patch = self.parser_patch
        o_clear_patch = None
        while o_patch is not None and o_patch.is_done == 1:
            # 这里做一次浅复制，因为解析保存的数据是单例模式，输出后会清理就数据
            d_patch = {}
            d_patch.update(o_patch.patch_file_data)
            d_result[o_patch.version] = {
                "V": o_patch.version,
                "A": o_patch.author,
                "D": o_patch.date,
                "M": o_patch.message,
                "P": d_patch
            }
            if not is_keep:
                keep_num -= 1
                if keep_num <= 0:
                    o_clear_patch = o_patch
            o_patch = o_patch.next_patch
        if o_clear_patch:
            o_clear_patch.next_patch = None
        return d_result


class Patch(object):
    def __init__(self):
        self.next_patch = None
        self.version = 0
        self.author = ""
        self.date = ""
        self.message = ""
        self.is_done = 0
        self.patch_file_data = {}

    def init(self):
        self.version = 0
        self.author = ""
        self.date = ""
        self.message = ""
        self.is_done = 0
        self.patch_file_data = {}
