import os

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DATA_DIR=os.path.join(BASE_DIR, 'data')

# IO相关设置
MIN_TOKENS = 100  # 过短的段落要合并
TARGET_TOKENS = 300  # 目标 chunk 大小
MAX_TOKENS = 500  # 超长的 chunk 需要拆分