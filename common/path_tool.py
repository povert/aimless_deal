# -*- coding: utf-8 -*-
import os
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
        elif re.match(r'([-\d]+)~([-\d]+)', group):
            start, end = map(int, group.split('~'))
            if start < 0:
                start = len(file_path_list) + start
            if end < 0:
                end = len(file_path_list) + end
            if start > end:
                start, end = end, start
            if end - start == 1:
                value = f'{file_path_list[start]}/{file_path_list[end]}'
            else:
                value = f'{file_path_list[start]}/*/{file_path_list[end]}'
            result.append(value)
    return result


def get_parent_basename(file_path: str, parent_level: int = 1):
    parent_path = file_path
    for i in range(parent_level):
        parent_path = os.path.dirname(parent_path)
    parent_basename = os.path.basename(parent_path)
    return parent_basename
