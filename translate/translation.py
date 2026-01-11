import os
import re
import logging
import json

from pathlib import Path
from langdetect import detect, DetectorFactory


class Translation:
    def __init__(self, translator, max_word_length=4500, log_output=None):
        DetectorFactory.seed = 0
        self.translator = translator
        self.max_word_length = max_word_length
        # 0-不输出，1-输出到文件，2-输出到控制台，3-自定义输出函数
        self.log_mode = 0
        self.log_obj = None
        if log_output is None:
            self.log_mode = 2
        elif isinstance(log_output, (str, bytes, os.PathLike)) and os.path.isfile(log_output):
            self.log_mode = 1
            self.log_obj = logging.getLogger(os.path.basename(log_output))
            self.log_obj.setLevel(logging.INFO)
            file_handler = logging.FileHandler(log_output)
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            self.log_obj.addHandler(file_handler)
        elif callable(log_output):
            self.log_mode = 3
            self.log_obj = log_output

    @staticmethod
    def detect(text):
        lang = detect(text)
        return {'zh-cn': 'zh'}.get(lang, lang)

    def logs(self, message):
        if self.log_mode == 0:
            return
        if self.log_mode == 1:
            self.log_obj.info(message)
        elif self.log_mode == 2:
            print(message)
        elif self.log_mode == 3:
            self.log_obj(message)

    def analyze_language(self, text, source_lang, target_lang):
        if source_lang == 'auto':
            source_lang = self.detect(text)
        if target_lang == 'auto':
            if source_lang == 'en':
                target_lang = 'zh'
            elif source_lang == 'zh':
                target_lang = 'en'
        if source_lang == 'auto' or target_lang == 'auto':
            return ValueError(f'cant detect language from text {source_lang} and {target_lang}')
        source_lang = self.translator.cover_language(source_lang)
        target_lang = self.translator.cover_language(target_lang)
        return source_lang, target_lang

    def split_text(self, text):
        if len(text) <= self.max_word_length:
            return [text]
        chunks = []
        # 按句子切分的分割符
        sentence_endings = ['.', '!', '?', '。', '！', '？', '\n', '；', ';', '：', ':']
        # 按字符逐个处理
        sentences = []
        current_sentence = ''
        for char in text:
            current_sentence += char
            if char in sentence_endings:
                sentences.append(current_sentence)
                current_sentence = ''
        if current_sentence:
            sentences.append(current_sentence)

        # 将句子组合成块
        current_chunk = sentences[0]
        for sentence in sentences[1:]:
            if len(current_chunk + sentence) <= self.max_word_length:
                current_chunk += sentence
            else:
                chunks.append(current_chunk)
                current_chunk = sentence
        if current_chunk:
            chunks.append(current_chunk)
        return chunks

    def translate_text(self, text, source_lang='auto', target_lang='auto'):
        source_lang, target_lang = self.analyze_language(text, source_lang, target_lang)
        chunks = self.split_text(text)
        translated_chunks = []
        for i, chunk in enumerate(chunks):
            self.logs(f'translate chunk {i+1}/{len(chunks)}')
            res = self.translator.translate(chunk, source_lang, target_lang)
            translated_chunks.append(res)
        return ''.join(translated_chunks)

    def translate_file(self, file_path, source_lang='auto', target_lang='auto', save_file=None):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        source_lang, target_lang = self.analyze_language(text, source_lang, target_lang)
        chunks = self.split_text(text)
        translated_chunks = []
        for i, chunk in enumerate(chunks):
            self.logs(f'translate chunk {i+1}/{len(chunks)}')
            res = self.translator.translate(chunk, source_lang, target_lang)
            translated_chunks.append(res)
        if not save_file:
            file_path = Path(file_path)
            save_file = file_path.with_name(f"{file_path.stem}_{target_lang}{file_path.suffix}")
        with open(save_file, 'w', encoding='utf-8') as f:
            f.write(''.join(translated_chunks))
        return save_file

    def translate_folder(self, folder_path, source_lang='auto', target_lang='auto', file_types=None):
        if not file_types:
            file_types = ['txt', 'json', 'jsonl']
        save_dirs = folder_path + '_translated'
        os.makedirs(save_dirs, exist_ok=True)
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.split('.')[-1] in file_types:
                    continue
                self.logs(f'translate file {file}')
                save_file = os.path.join(save_dirs, file)
                self.translate_file(file, source_lang, target_lang, save_file)
        return save_dirs

    def translate_json(self, json_path, source_lang='auto', target_lang='auto', save_file=None):
        with open(json_path, 'r', encoding='utf-8') as f:
            text = f.read()
        source_lang, target_lang = self.analyze_language(text, source_lang, target_lang)
        json_obj = json.loads(text)
        string_list = []
        def _replace(obj):
            if isinstance(obj, dict):
                return {k: _replace(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [_replace(item) for item in obj]
            elif isinstance(obj, str):
                record_index = len(string_list)
                string_list.append(obj.strip())
                return f"【《{record_index}》】"
            return obj

        def _restore(obj):
            if isinstance(obj, dict):
                return {k: _restore(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [_restore(item) for item in obj]
            elif isinstance(obj, str):
                math = re.fullmatch(r'【《(\d+)》】', obj)
                if math:
                    record_index = int(math.group(1))
                    return string_list[record_index]
            return obj

        json_obj = _replace(json_obj)
        if not string_list:
            return 'no string to translate'
        merge_index = []
        merge_sentence = ''
        split_flag = '\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n\n'
        split_length = len(string_list)
        for i, sentence in enumerate(string_list):
            if len(sentence) >= self.max_word_length:
                self.logs(f'translate sentence {i+1}/{len(string_list)}')
                string_list[i] = self.translate_text(sentence, source_lang, target_lang)
                continue
            if len(merge_sentence + sentence) <= self.max_word_length - split_length:
                if not merge_index:
                    merge_sentence = sentence
                else:
                    merge_sentence += split_flag + sentence
                merge_index.append(i)
            elif not merge_index:
                merge_sentence = sentence
                merge_index = [i]
            else:
                self.logs(f'translate merger sentence {merge_index}/{len(string_list)}')
                translate_sentence = self.translator.translate(merge_sentence, source_lang, target_lang)
                translate_sentence_list = translate_sentence.split(split_flag)
                if len(translate_sentence_list) != len(merge_index):
                    self.logs(f'translate sentencr err {len(translate_sentence_list)} != {len(merge_index)}')
                    self.logs(merge_sentence)
                    raise Exception('translate sentence error')
                for tr_idx, re_idx in enumerate(merge_index):
                    string_list[re_idx] = translate_sentence_list[tr_idx]
                merge_sentence = sentence
                merge_index = [i]
        if merge_index:
            self.logs(f'translate merger sentence {merge_index}/{len(string_list)}')
            self.logs(f'translate merger sentence {merge_index}/{len(string_list)}')
            translate_sentence = self.translator.translate(merge_sentence, source_lang, target_lang)
            translate_sentence_list = translate_sentence.split(split_flag)
            if len(translate_sentence_list) != len(merge_index):
                self.logs(f'translate sentencr err {len(translate_sentence_list)} != {len(merge_index)}')
                self.logs(merge_sentence)
                raise Exception('translate sentence error')
            for tr_idx, re_idx in enumerate(merge_index):
                string_list[re_idx] = translate_sentence_list[tr_idx]
        json_obj = _restore(json_obj)
        if not save_file:
            file_path = Path(json_path)
            save_file = file_path.with_name(f"{file_path.stem}_{target_lang}{file_path.suffix}")
        with open(save_file, 'w', encoding='utf-8') as f:
            json.dump(json_obj, f, ensure_ascii=False, indent=4)
        return save_file

