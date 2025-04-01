# -*- coding: utf-8 -*-
import os
import json

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
    file_stack = [(file_path, 0)]
    while file_stack:
        node_path, node_depth = file_stack.pop(0)
        if node_depth == depth:
            subdirs.append(node_path)
            continue
        is_over = True
        for path in os.listdir(node_path):
            abs_path = os.path.join(node_path, path)
            if os.path.isdir(abs_path):
                file_stack.append((abs_path, node_depth + 1))
                is_over = False
        if keep_no_enouht and is_over:
            subdirs.append(node_path)
    return subdirs


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


