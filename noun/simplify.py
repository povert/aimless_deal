# -*- coding: utf-8 -*-
import re
import jieba
import jieba.posseg as psg

# 名称简化，方便转换为英文变量命名

class SimplifyModel:
    extract_tag = {'n', 'v', 'vn', 'eng', 'uj', 'j', 'x', 'b'}

    def __init__(self, noun):
        self.noun = noun
        self.simplify_noun = ''
        self._psg_list = list(psg.cut(noun))
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
        format_rule2 = ['v-n', 'vn-n', 'n-n', 'vn']
        format_rule3 = ['n-n-n', ]
        format_rule4 = ['nv']
        if format_noun in format_rule1:
            self.simplify_noun = self.noun
        elif format_noun in format_rule2:
            self.simplify_noun = self.noun_group[-1][1]
        elif format_noun in format_rule3:
            word1, word2 = self.noun_group[2][1], self.noun_group[-1][1]
            self.simplify_noun = word1 + word2
        elif format_noun in format_rule4:
            self.simplify_noun = self.noun_group[0][1]

    def _rm_extra_noun(self):
        if re.match(r'.+列表.+', self.simplify_noun):
            rm_extra = re.match(r'.+列表(.+)', self.simplify_noun).group(1)
            self.simplify_noun = re.sub(rm_extra, '', self.simplify_noun)

class AnalyzeModel:
    def __init__(self, noun):
        self.noun = noun
        self._psg_list = list(psg.cut(noun))
        self.analyze()

    def analyze(self):
        self._split_noun()
        if len(self.noun_group) == 1 and re.search(r'和|与|、', self.noun):
            self._split_noun2()
        self._add_extra_noun()

    def _split_noun(self):
        self.split_group = []
        cur_group = []
        for (w, c) in self._psg_list:
            if c != 'n' and not cur_group:
                self.split_group.append(['p', w])
            elif w in {'和', '与', '、'} or c == 'c':
                self.split_group.append(cur_group)
                self.split_group.append(['-', w])
                cur_group = []
            else:
                if not cur_group:
                    cur_group = ['n', '']
                cur_group[1] += w
        if cur_group:
            self.split_group.append(cur_group)
        self.noun_group = [w for (c, w) in self.split_group if c == 'n']

    def _split_noun2(self):
        split_group = re.split(r'和|与|、', self.noun)
        self.noun_group = []
        index = 0
        for split_noun in split_group:
            index += 1
            deal_noun = ""
            for (w, c) in psg.cut(split_noun):
                if not deal_noun and not c in {'n', 'eng', 'vn', 'v'} and index == 1:
                    continue
                deal_noun += w
            if deal_noun:
                self.noun_group.append(deal_noun)

    def _add_extra_noun(self):
        if re.match(r'.+的.+', self.noun_group[-1]):
            add_noun = re.match(r'.+(的.+)', self.noun_group[-1]).group(1)
            for i in range(len(self.noun_group) - 1):
                self.noun_group[i] += add_noun

