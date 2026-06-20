import re
from typing import Any, Dict, List, Tuple, Union
from langdetect import detect as _detect, DetectorFactory

def split_text(text: str, max_word_length: int) -> List[str]:
    """Split text into chunks not exceeding max_word_length."""
    if len(text) <= max_word_length:
        return [text]
    chunks = []
    sentence_endings = ['.', '!', '?', '。', '！', '？', '\n', '；', ';', '：', ':']
    sentences = []
    current_sentence = ''
    for char in text:
        current_sentence += char
        if char in sentence_endings:
            sentences.append(current_sentence)
            current_sentence = ''
    if current_sentence:
        sentences.append(current_sentence)

    current_chunk = sentences[0]
    for sentence in sentences[1:]:
        if len(current_chunk + sentence) <= max_word_length:
            current_chunk += sentence
        else:
            chunks.append(current_chunk)
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def detect(text: str) -> str:
    """Detect language of text, normalizing zh-cn to zh."""
    DetectorFactory.seed = 0
    lang = _detect(text)
    return {'zh-cn': 'zh'}.get(lang, lang)

def replace_strings(obj: Any, string_list: List[str], placeholder_pattern: str = '【《{index}》】') -> Any:
    """Recursively replace strings in JSON object with placeholders, collecting strings in string_list."""
    if isinstance(obj, dict):
        return {k: replace_strings(v, string_list, placeholder_pattern) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_strings(item, string_list, placeholder_pattern) for item in obj]
    elif isinstance(obj, str):
        record_index = len(string_list)
        string_list.append(obj.strip())
        return placeholder_pattern.format(index=record_index)
    return obj

def restore_strings(obj: Any, string_list: List[str], placeholder_pattern: str = '【《(\\d+)》】') -> Any:
    """Recursively restore strings in JSON object from placeholders using string_list."""
    if isinstance(obj, dict):
        return {k: restore_strings(v, string_list, placeholder_pattern) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [restore_strings(item, string_list, placeholder_pattern) for item in obj]
    elif isinstance(obj, str):
        math = re.fullmatch(placeholder_pattern, obj)
        if math:
            record_index = int(math.group(1))
            return string_list[record_index]
    return obj

def infer_target_language(source_lang: str) -> str:
    """Infer target language based on source language."""
    if source_lang == 'en':
        return 'zh'
    elif source_lang == 'zh':
        return 'en'
    return 'auto'