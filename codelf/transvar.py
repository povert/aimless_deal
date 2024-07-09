# -*- coding: utf-8 -*-
import os
import jieba
import re

current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)

class Translater:

    def __init__(self):
        self._chinese_to_eng = {}
        self._cant_translate = []
        self.load_dict()

    def load_dict(self):
        data_dir_path = f'{current_dir_path}/dictdata'
        for file in os.listdir(data_dir_path):
            file_name = os.path.join(data_dir_path, file)
            if not file.endswith(".dat"):
                continue
            with open(file_name, 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    lines = re.split(',|，', line)
                    if len(lines) < 2:
                        continue
                    chinese_word = lines[0].strip()
                    if chinese_word not in self._chinese_to_eng:
                        self._chinese_to_eng[chinese_word] = lines[1].strip()
                        continue
                    if file.startswith("custom"):  # 自定义数据字典可以覆盖其他字典数据
                        self._chinese_to_eng[chinese_word] = lines[1].strip()
                        continue
                    if len(lines[1]) < len(self._chinese_to_eng[chinese_word]):
                        self._chinese_to_eng[chinese_word] = lines[1].strip()
        print(f'载入数据{len(self._chinese_to_eng)}条')

    def treanslateC(self, chinese_word):
        if chinese_word in self._chinese_to_eng:
            return self._chinese_to_eng[chinese_word]
        word_list = list(jieba.lcut(chinese_word))
        preeng_result = []
        result = []
        poseng_result = []
        for word in word_list:
            if word in self._chinese_to_eng:
                result.append(self._chinese_to_eng[word])
            elif f"使{word}" in self._chinese_to_eng:
                result.append(self._chinese_to_eng[f"使{word}"])
            elif f"{word}的" in self._chinese_to_eng:
                result.append(self._chinese_to_eng[f"{word}的"])
            elif f"{word}地" in self._chinese_to_eng:
                result.append(self._chinese_to_eng[f"{word}地"])
            elif re.match(r'^[a-zA-Z]+$', word):
                if not result:
                    preeng_result.append(word.lower())
                else:
                    poseng_result.append(word.lower())
        result = preeng_result + result + poseng_result
        if not result:      # 保底翻译成信息数据
            result.append("info_data")
            self._cant_translate.append(chinese_word)
        return '_'.join(result)

    def record_cant_translate(self):
        has_recod = False
        file_name = f'{current_dir_path}/cant_translate.dat'
        with open(file_name, 'a+', encoding='utf-8') as f:
            for word in set(self._cant_translate):
                word = word.strip()
                if not word:
                    continue
                f.write(f"{word},\n")
                has_recod = True
        if has_recod:
            print(f"存在无法翻译字段，记录在{file_name}, 可手动处理")






