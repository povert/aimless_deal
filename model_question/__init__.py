# -*- coding: utf-8 -*-
import os

# 设置大模型询问内容缓存目录
os.environ['MODEL_CACHE_DIR'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.cache')
