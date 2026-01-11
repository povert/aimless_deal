# -*- coding: utf-8 -*-
import os

from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer



class Translator_HelsinkiNLP:
    model_name_en_zh = "Helsinki-NLP/opus-mt-en-zh"
    model_name_zh_en = "Helsinki-NLP/opus-mt-zh-en"

    def __init__(self):
        self.en_zh_model = None
        self.zh_en_model = None
        self.en_zh_tokenizer = None
        self.zh_en_tokenizer = None


    def translate(self, text, source_language, target_language):
        if source_language == 'en' and target_language == 'zh':
            return self.translate_en_zh(text)
        elif source_language == 'zh' and target_language == 'en':
            return self.translate_zh_en(text)
        raise ValueError(f'only support zh<->en, not {source_language}->{target_language}')

    def translate_en_zh(self, text):
        if not self.en_zh_model:
            model, tokenizer = load_model(self.model_name_en_zh)
            self.en_zh_model = model
            self.en_zh_tokenizer = tokenizer
        inputs = self.en_zh_tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        outputs = self.en_zh_model.generate(
            **inputs,
            max_length=512,
            num_beams=4,
            length_penalty=1.0,
            early_stopping=True
        )
        trans_res = self.en_zh_tokenizer.decode(outputs[0], skip_special_tokens=True)
        return trans_res

    def translate_zh_en(self, text):
        if not self.zh_en_model:
            model, tokenizer = load_model(self.model_name_zh_en)
            self.zh_en_model = model
            self.zh_en_tokenizer = tokenizer
        inputs = self.zh_en_tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        outputs = self.zh_en_model.generate(
            **inputs,
            max_length=512,
            num_beams=4,
            length_penalty=1.0,
            early_stopping=True
        )
        trans_res = self.zh_en_tokenizer.decode(outputs[0], skip_special_tokens=True)
        return trans_res

    @staticmethod
    def cover_language(language):
        return language


class Translator_NLLB:
    model_name = "facebook/nllb-200-distilled-600M"

    def __init__(self):
        model, tokenizer = load_model(self.model_name)
        self.translator = pipeline("translation", model=model, tokenizer=tokenizer)

    def translate(self, text, source_language, target_language):
        result = self.translator(
            text,
            src_lang=source_language,
            tgt_lang=target_language,
            max_length=512  # 控制最大生成长度
        )
        trans_res = result[0]['translation_text']
        return trans_res

    @staticmethod
    def cover_language(language):
        lang_dict = {"en": "eng_Latn", "zh": "zho_Hans"}
        return lang_dict.get(language, language)


def load_model(model_name):
    os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
    os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
    cache_dir = os.environ.get('MODEL_SAVE_PATH', '.')
    print('Loading model...', cache_dir)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name, cache_dir=cache_dir)
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
    os.environ.pop('HTTP_PROXY')
    os.environ.pop('HTTPS_PROXY')
    return model, tokenizer
