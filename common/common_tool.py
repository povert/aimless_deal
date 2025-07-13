# -*- coding: utf-8 -*-
import os
import json
import re
from typing import List, Union


def write_jsonl_file(file_path: str, all_data: List[Union[dict, str]]) -> None:
    save_data = []
    for data in all_data:
        if isinstance(data, str):
            save_data.append(data)
        else:
            save_data.append(json.dumps(data, ensure_ascii=False))
    save_dir = os.path.dirname(file_path)
    if save_dir and not os.path.exists(save_dir):
        os.makedirs(save_dir)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(save_data))


def extract_chinese_in_english(text: str) -> List[dict]:
    extract_info = []
    start, end = -1, -1
    combination_symbols = ['[]', '【】', '{}', '<>', '()', '（）', '$$', '**', '""', "''"]
    regex = re.compile(r'[\u4e00-\u9fa5][\u4e00-\u9fa5,，.。;；?？:：]*[\u4e00-\u9fa5][,，.。;；?？]*')
    regex_cn = re.compile(r'[\u4e00-\u9fa5]')
    regex_en = re.compile(r'[a-zA-Z]+')
    for match in regex.finditer(text):
        if not regex_cn.search(match.group()):
            continue
        s, e = match.span()
        # 被组合符号包裹的中文需要将组合作为一个整体输出
        if s > 0 and e < len(text) and f'{text[s-1]}{text[e]}' in combination_symbols:
            s -= 1
            e += 1
        # 被引号包裹的中文不合并
        if f'{text[s]}{text[e-1]}' in ['""', "''"]:
            if start != -1:
                extract_info.append({'start': start, 'end': end})
            extract_info.append({'start': s, 'end': e})
            start, end = -1, -1
            continue
        if start == -1:
            start, end = s, e
            continue
        # 两个中文差距内容过大就不合并
        if s - end >= 20:
            extract_info.append({'start': start, 'end': end})
            start, end = s, e
            continue
        word = len([s for s in regex_en.findall(text[end:s])])
        # 两个中文之间存在大于1个单词也不做合并
        if word > 1:
            extract_info.append({'start': start, 'end': end})
            start, end = s, e
            continue
        # 不做跨行合并
        if '\n' in text[end:s]:
            extract_info.append({'start': start, 'end': end})
            start, end = s, e
            continue
        # 合并两个中文内容
        end = e
    if start != -1:
        extract_info.append({'start': start, 'end': end})
    return extract_info


def find_optimal_split_val(y, m, n):
    """返回区间[m,n]内使y分割最均匀的最大x值"""
    if n >= y: return n
    best_x = n
    min_diff = float('inf')
    for a in range(y // m, y // n - 1, -1):
        x = max(m, min(n, y // a))
        diff = y - a * x
        print(x, a, diff)
        if diff <= min_diff:
            min_diff, best_x = diff, x
    return best_x
