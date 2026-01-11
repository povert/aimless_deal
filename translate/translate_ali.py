import os

from alibabacloud_alimt20181012.client import Client as AlibaClient
from alibabacloud_tea_openapi import models as tea_models
from alibabacloud_alimt20181012 import models as alimt20181012_models


class AlibaTranslator:
    def __init__(self):
        config = tea_models.Config(
            access_key_id=os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID"),
            access_key_secret=os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET"),
            endpoint="mt.cn-hangzhou.aliyuncs.com",
        )
        self.client = AlibaClient(config)

    def translate(self, text, source_language, target_language):
        request = alimt20181012_models.TranslateRequest(
            source_text=text,
            source_language=source_language,
            target_language=target_language,
            format_type="text",
        )
        response = self.client.translate(request)
        res = response.body.data.translated
        return res

    @staticmethod
    def cover_language(language):
        return language