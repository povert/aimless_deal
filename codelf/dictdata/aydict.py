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
        line = line.strip()
        matches = re.search('([a-zA-Z]+),"?([^"]*)"?', line)
        if not matches:
            continue
        eng_word, eng_desc = matches.group(1), matches.group(2)
        if len(eng_word) <= 2:       # 小于两个字母的单词不考虑作为变量名处理
            continue
        chi_list = re.split(r'(vt\.|vi\.|n\.|adv\.|adj\.|prep\.|int\.|v\.|num\.)', eng_desc)[1:]
        for i in range(0, len(chi_list), 2):
            w_type = chi_list[i][:-1]
            if w_type == 'num':
                continue
            chi_words = chi_list[i+1]
            for chi_word in chi_words.split(','):
                chi_word = re.sub(r'\[[^\]]*\]|\([^)]*\)|<[^>]*>', '', chi_word).strip()
                if not chi_word:
                    continue
                if re.search(r'[^\u4e00-\u9fa5]', chi_word):
                    continue
                result_list.append(f'{chi_word},{eng_word},{w_type}\n')

with open(f'{current_dir_path}/aydict.dat', 'w', encoding='utf-8') as f:
    f.writelines(result_list)
print(f"解析完毕，共收集{len(result_list)}行数据")




