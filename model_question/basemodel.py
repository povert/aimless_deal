# -*- coding: utf-8 -*-
import os
import threading
from typing import List, Dict


def get_cache(cache_file: str) -> str:
    if not os.path.isabs(cache_file):
        cache_dir = os.environ.get('MODEL_CACHE_DIR')
        cache_file = os.path.join(cache_dir, cache_file)
    if os.path.exists(cache_file):
        return ''
    with open(cache_file, 'r', encoding='utf-8') as f:
        text = f.read()
    return text


def record_cache(cache_file: str, cache_text: str) -> None:
    if not os.path.isabs(cache_file):
        cache_dir = os.environ.get('MODEL_CACHE_DIR')
        cache_file = os.path.join(cache_dir, cache_file)
    cache_dir = os.path.dirname(cache_file)
    if cache_dir and not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    with open(cache_file, 'w', encoding='utf-8') as f:
        f.write(cache_text)


class BaseModel:
    NAME = ''

    @classmethod
    def chat(cls, user_content: str, system_content: str='', flag: str='', timeout: int=0, cache_file: str='') -> str:
        if cache_file:
            cache_text = get_cache(cache_file)
            if cache_text:
                return cache_text
        result, text = [], ''
        messages = [{'role': 'user', 'content': user_content}]
        if system_content:
            messages.insert(0, {'role': 'system', 'content': system_content})
        if timeout:
            event = threading.Event()
            t = threading.Thread(target=cls._chat, args=(messages, result, flag, event))
            t.daemon = True
            t.start()
            event.wait(timeout=timeout)
        else:
            cls._chat(messages, result, flag)
        if result:
            text = result[0]
        if text and cache_file:
            record_cache(cache_file, text)
        return text

    @classmethod
    def _chat(cls, messages: List[Dict[str, str]], result: List[str], flag: str='', event: threading.Event=None) -> None:
        try:
            cls.get_result(messages, result)
        except Exception as e:
            print(f'{cls.NAME} {flag} 出现错误：{type(e).__name__} {e}')
        finally:
            if event:
                event.set()

    @classmethod
    def get_result(cls, messages: List[Dict[str, str]], result: List[str]) -> None:
        pass