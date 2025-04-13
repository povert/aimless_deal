# -*- coding: utf-8 -*-
import os
import json
import re

from typing import List, Union


def get_file_path_with_type(file_path: str, file_type: str) -> List[str]:
    file_list = []
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if not file.endswith(file_type):
                continue
            if file_type.endswith('xlsx') and file.startswith('~'):
                continue
            file_list.append(os.path.join(root, file))
    return file_list


def get_subdirs_with_depth(file_path: str, depth: str, keep_no_enouht: bool = True) -> List[str]:
    subdirs = []
    file_queue = [(file_path, 0)]
    while file_queue:
        node_path, node_depth = file_queue.pop(0)
        if node_depth == depth:
            subdirs.append(node_path)
            continue
        is_over = True
        for path in os.listdir(node_path):
            abs_path = os.path.join(node_path, path)
            if os.path.isdir(abs_path):
                file_queue.append((abs_path, node_depth + 1))
                is_over = False
        if keep_no_enouht and is_over:
            subdirs.append(node_path)
    return subdirs


def find_full_path_by_parts(file_path: str, parts: List[str], max_depth: int = 7):
    find_part = parts.pop(0)
    file_queue = [(file_path, 0)]
    while file_queue:
        node_path, node_depth = file_queue.pop(0)
        if node_depth == max_depth:
            continue
        all_dirs = [d for d in os.listdir(node_path) if os.path.isdir(os.path.join(node_path, d))]
        if find_part not in all_dirs:
            file_queue.extend([(os.path.join(node_path, d), node_depth+1) for d in all_dirs])
        else:
            new_node_path = os.path.join(node_path, find_part)
            if not parts:
                return new_node_path
            else:
                file_queue.append((new_node_path, node_depth+1))
                find_part = parts.pop(0)
    return None


def get_file_path_groups(file_path: str, groups: List[Union[int, str]]) -> List[str]:
    file_path_list = [sep_path for sep_path in file_path.split('/')[:-1] if sep_path]
    result: List[str] = []
    for group in groups:
        if isinstance(group, int):
            result.append(file_path_list[group])
            continue
        if isinstance(group, str):
            match_result = re.match(r'(\d+)-(\d+)', group)
            if match_result:
                group = range(int(match_result.group(1)), int(match_result.group(2)) + 1)
        last_g = -1
        s = ''
        for g in group:
            if g == 0:
                s += f'/{file_path_list[g]}'
            elif last_g != -1 and g - last_g == 1:
                s += f'/{file_path_list[g]}'
            elif last_g == -1:
                s = file_path_list[g]
            else:
                s += f'/*/{file_path_list[g]}'
            last_g = g
        result.append(s)
    return result


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
