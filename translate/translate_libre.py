# -*- coding: utf-8 -*-
import requests


def translate_en_zh(text):
    return run_translate(text, "en", "zh")


def translate_zh_en(text):
    return run_translate(text, "zh", "en")


def run_translate(text, source_language, target_language):
    url = "http://localhost:5000/translate"
    headers = {"Content-Type": "application/json"}
    json_data = {
        "q": text,
        "source": source_language,
        "target": target_language
    }
    response = requests.post(url, headers=headers, json=json_data)
    data = response.json()
    return data["translatedText"]
