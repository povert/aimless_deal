import os
import logging
import json

from typing import Any, Callable, List, Optional, Protocol, Tuple, Union
from pathlib import Path
from . import util


class Translator(Protocol):
    def translate(self, text: str, source_lang: str, target_lang: str) -> str: ...
    def cover_language(self, language: str) -> str: ...


LogCallback = Callable[[str], None]
LogOutput = Union[None, str, bytes, os.PathLike, LogCallback]


class Translation:
    def __init__(self, translator: Translator, max_word_length: int = 4500, log_output: LogOutput = None) -> None:
        self.translator: Translator = translator
        self.max_word_length: int = max_word_length
        # 0-不输出，1-输出到文件，2-输出到控制台，3-自定义输出函数
        self.log_mode: int = 0
        self.log_obj: Union[None, logging.Logger, LogCallback] = None
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

    def logs(self, message: str) -> None:
        if self.log_mode == 0:
            return
        if self.log_mode == 1:
            assert isinstance(self.log_obj, logging.Logger)
            self.log_obj.info(message)
        elif self.log_mode == 2:
            print(message)
        elif self.log_mode == 3:
            assert callable(self.log_obj)
            self.log_obj(message)

    def analyze_language(self, text: str, source_lang: str, target_lang: str) -> Tuple[str, str]:
        if source_lang == 'auto':
            source_lang = util.detect(text)
        if target_lang == 'auto':
            target_lang = util.infer_target_language(source_lang)
        if source_lang == 'auto' or target_lang == 'auto':
            raise ValueError(f'cant detect language from text {source_lang} and {target_lang}')
        source_lang = self.translator.cover_language(source_lang)
        target_lang = self.translator.cover_language(target_lang)
        return source_lang, target_lang

    def split_text(self, text: str) -> List[str]:
        return util.split_text(text, self.max_word_length)

    def translate_text(self, text: str, source_lang: str = 'auto', target_lang: str = 'auto') -> str:
        result = self.analyze_language(text, source_lang, target_lang)
        source_lang, target_lang = result
        chunks: List[str] = self.split_text(text)
        translated_chunks: List[str] = []
        for i, chunk in enumerate(chunks):
            self.logs(f'translate chunk {i+1}/{len(chunks)}')
            res = self.translator.translate(chunk, source_lang, target_lang)
            translated_chunks.append(res)
        return ''.join(translated_chunks)

    def translate_json(self, json_obj: Any, source_lang: str = 'auto', target_lang: str = 'auto') -> Any:
        string_list: List[str] = []
        json_obj = util.replace_strings(json_obj, string_list)
        if not string_list:
            return json_obj
        split_flag: str = '\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n\n'
        split_length: int = len(string_list)
        merge_index: List[int] = []
        merge_sentence: str = ''
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
                    self.logs(f'translate sentence err {len(translate_sentence_list)} != {len(merge_index)}')
                    self.logs(merge_sentence)
                    raise Exception('translate sentence error')
                for tr_idx, re_idx in enumerate(merge_index):
                    string_list[re_idx] = translate_sentence_list[tr_idx]
                merge_sentence = sentence
                merge_index = [i]
        if merge_index:
            self.logs(f'translate merger sentence {merge_index}/{len(string_list)}')
            translate_sentence = self.translator.translate(merge_sentence, source_lang, target_lang)
            translate_sentence_list = translate_sentence.split(split_flag)
            if len(translate_sentence_list) != len(merge_index):
                self.logs(f'translate sentence err {len(translate_sentence_list)} != {len(merge_index)}')
                self.logs(merge_sentence)
                raise Exception('translate sentence error')
            for tr_idx, re_idx in enumerate(merge_index):
                string_list[re_idx] = translate_sentence_list[tr_idx]
        return util.restore_strings(json_obj, string_list)

    def translate_file(self, file_path: str, source_lang: str = 'auto', target_lang: str = 'auto', save_file: Optional[str] = None) -> Path:
        ext = Path(file_path).suffix.lower()
        save_path = Path(save_file) if save_file else Path(file_path).with_name(f"{Path(file_path).stem}_{target_lang}{Path(file_path).suffix}")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if not content.strip():
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return save_path
        if ext == '.json':
            source_lang, target_lang = self.analyze_language(content, source_lang, target_lang)
            json_obj = json.loads(content)
            translated_obj = self.translate_json(json_obj, source_lang, target_lang)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(translated_obj, f, ensure_ascii=False, indent=4)
            return save_path
        if ext == '.jsonl':
            lines = content.splitlines(keepends=True)
            sample = lines[0].strip() if lines else ''
            if sample:
                source_lang, target_lang = self.analyze_language(sample, source_lang, target_lang)
            translated_lines: List[str] = []
            for i, line in enumerate(lines):
                stripped = line.rstrip('\n')
                if not stripped:
                    translated_lines.append('')
                    continue
                json_obj = json.loads(stripped)
                translated_obj = self.translate_json(json_obj, source_lang, target_lang)
                self.logs(f'translate jsonl line {i+1}/{len(lines)}')
                translated_lines.append(json.dumps(translated_obj, ensure_ascii=False))
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(translated_lines))
            return save_path

        source_lang, target_lang = self.analyze_language(content, source_lang, target_lang)
        translated = self.translate_text(content, source_lang, target_lang)
        save_path = Path(save_file) if save_file else Path(file_path).with_name(f"{Path(file_path).stem}_{target_lang}{Path(file_path).suffix}")
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(translated)
        return save_path

    def translate_folder(self, folder_path: str, source_lang: str = 'auto', target_lang: str = 'auto', file_types: Optional[List[str]] = None) -> str:
        if not file_types:
            file_types = ['txt', 'json', 'jsonl']
        save_dirs: str = folder_path + '_translated'
        os.makedirs(save_dirs, exist_ok=True)
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.split('.')[-1] not in file_types:
                    continue
                self.logs(f'translate file {file}')
                save_file = os.path.join(save_dirs, file)
                self.translate_file(os.path.join(root, file), source_lang, target_lang, save_file)
        return save_dirs


