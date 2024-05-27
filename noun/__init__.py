# -*- coding: utf-8 -*-
import os
import jieba
import noun.simplify as simplify

current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)
custom_jieba_file = os.path.join(current_dir_path, 'jiebadata/custom_jieba.txt')
jieba.load_userdict(custom_jieba_file)

def simplify_noun(noun):
    model = simplify.SimplifyModel(noun)
    return model.simplify_noun