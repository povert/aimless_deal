# -*- coding: utf-8 -*-
import requests


class LibreTranslator:

    @staticmethod
    def translate(text, source_language, target_language):
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

    @staticmethod
    def cover_language(language):
        return language