# -*- coding: utf-8 -*-
import re
import jieba
import jieba.posseg as psg

# 名称简化，方便转换为英文变量命名

class SimplifyModel:
    extract_tag = {'n', 'v', 'vn', 'eng', 'uj', 'j', 'x'}

    def __init__(self, noun):
        self.noun = noun
        self.simplify_noun = ''
        self._psg_list = psg.cut(noun)
        self.simplify()

    def simplify(self):
        self._split_noun()
        self._match_noun()
        self._rm_extra_noun()

    def _split_noun(self):
        extract_noun = [(w, c) for (w, c) in self._psg_list if c in self.extract_tag]
        self.noun_group = []
        cur_group = []
        for (w, c) in extract_noun:
            if c in {'eng', 'x', 'vn'}: c = 'n'
            elif c in {'uj', 'j'}: c = '-'
            if not cur_group: cur_group = [c, w]
            elif cur_group[0] == c: cur_group[1] += w
            else:
                self.noun_group.append(cur_group)
                cur_group = [c, w]
        if cur_group: self.noun_group.append(cur_group)

    def _match_noun(self):
        format_noun = ''.join([c for (c, _) in self.noun_group])
        format_rule1 = ['n', ]
        format_rule2 = ['v-n', 'n-n', 'vn']
        format_rule3 = ['n-n-n', ]
        if format_noun in format_rule1:
            self.simplify_noun = self.noun
        elif format_noun in format_rule2:
            self.simplify_noun = self.noun_group[-1][1]
        elif format_noun in format_rule3:
            word1, word2 = self.noun_group[2][1], self.noun_group[-1][1]
            self.simplify_noun = word1 + word2

    def _rm_extra_noun(self):
        if re.match(r'.+列表.+', self.simplify_noun):
            rm_extra = re.match(r'.+列表(.+)', self.simplify_noun).group(1)
            self.simplify_noun = re.sub(rm_extra, '', self.simplify_noun)



