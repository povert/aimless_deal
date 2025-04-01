# -*- coding: utf-8 -*-
import os

from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer


def load_model(model_name):
    os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
    os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
    cache_dir = os.environ.get('MODEL_SAVE_PATH', '.')
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name, cache_dir=cache_dir)
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
    os.environ.pop('HTTP_PROXY')
    os.environ.pop('HTTPS_PROXY')
    return model, tokenizer


class Translator_HelsinkiNLP():
    model_name_en_zh = "Helsinki-NLP/opus-mt-en-zh"
    model_name_zh_en = "Helsinki-NLP/opus-mt-zh-en"

    def __init__(self):
        self.en_zh_model = None
        self.zh_en_model = None
        self.en_zh_tokenizer = None
        self.zh_en_tokenizer = None


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


class Translator_NLLB():
    model_name = "facebook/nllb-200-distilled-600M"

    def __init__(self):
        self.translator = None

    def translate_en_zh(self, text):
        if not self.translator:
            model, tokenizer = load_model(self.model_name)
            self.translator = pipeline("translation", model=model, tokenizer=tokenizer)
        result = self.translator(
            text,
            src_lang="eng_Latn",
            tgt_lang="zho_Hans",
            max_length=512  # 控制最大生成长度
        )
        trans_res = result[0]['translation_text']
        return trans_res

    def translate_zh_en(self, text):
        if not self.translator:
            model, tokenizer = load_model(self.model_name)
            self.translator = pipeline("translation", model=model, tokenizer=tokenizer)
        result = self.translator(
            text,
            src_lang="zho_Hans",
            tgt_lang="eng_Latn",
            max_length=512  # 控制最大生成长度
        )
        trans_res = result[0]['translation_text']
        return trans_res
