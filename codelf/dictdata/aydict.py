# -*- coding: utf-8 -*-
import os
import re

# 将简明英汉字典文件内容重新提前处理成汉字，英文，词性类型，方便后续读取使用
current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)
dict_file_name = f'{current_dir_path}/简明英汉词典（vivo_edited）.csv'
result_list = []
with open(dict_file_name, 'r', encoding='utf-8') as f:
    for line in f.readlines():
        matches = re.findall(r'(\b[a-z]+\b(?:,\w+)?)\s*,\s*"([^"]+)"', line)
        split_line = matches[0] if matches else line.split(',')
        if len(split_line) != 2:
            break
        eng_word, eng_desc = split_line
        if len(eng_word) <= 2:       # 小于两个字母的单词不考虑作为变量名处理
            continue
        matches = re.findall(r'(vt\.|vi\.|n\.|adv\.|adj\.|prep\.|)(.*)', eng_desc)
        for part_of_speech, content in matches:
            content = re.sub(r'\[[^\]]*\]|\([^)]*\)|<[^>]*>', '', content).strip()
            for chinese_word in re.split(r' |,|\.', content):
                if not chinese_word:
                    continue
                if re.search(r'[^\u4e00-\u9fa5]', chinese_word):
                    continue
                result_list.append(f'{chinese_word},{eng_word},{part_of_speech[:-1]}\n')

with open(f'{current_dir_path}/aydict.dat', 'w', encoding='utf-8') as f:
    f.writelines(result_list)
print(f"解析完毕，共收集{len(result_list)}行数据")








