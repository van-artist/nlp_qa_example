import re

# 设定 chunk 长度范围
MIN_TOKENS = 100  # 过短的段落要合并
TARGET_TOKENS = 300  # 目标 chunk 大小
MAX_TOKENS = 500  # 超长的 chunk 需要拆分

def tokenize(text):
    """ 简单的 token 计数器（这里假设1汉字=1token，英文空格分词）"""
    return list(text)

def count_tokens(text):
    """ 计算文本的 token 数量 """
    return len(tokenize(text))

def split_long_text(text, max_length=MAX_TOKENS):
    """
    如果文本过长，按照句号、换行或逗号拆分，确保每块 <= max_length
    """
    sentences = re.split(r'(。|！|？|\n)', text)  # 以主要标点符号或换行分割
    chunks, current_chunk = [], ""

    for sentence in sentences:
        if not sentence.strip():  # 跳过空句子
            continue
        if count_tokens(current_chunk + sentence) > max_length:
            chunks.append(current_chunk)
            current_chunk = sentence
        else:
            current_chunk += sentence

    if current_chunk:  # 添加最后的 chunk
        chunks.append(current_chunk)
    
    return chunks

def adjust_chunks(paragraphs):
    """
    遍历原始段落列表，进行：
    1. 过短的段落合并
    2. 过长的段落拆分
    """
    adjusted_chunks = []
    buffer = ""

    for para in paragraphs:
        para_tokens = count_tokens(para)

        if para_tokens > MAX_TOKENS:
            # 过长的段落，拆分
            adjusted_chunks.extend(split_long_text(para, MAX_TOKENS))
        elif para_tokens < MIN_TOKENS:
            # 过短的段落，先暂存到 buffer 里
            buffer += para
            if count_tokens(buffer) >= MIN_TOKENS:
                adjusted_chunks.append(buffer)
                buffer = ""
        else:
            # 正常长度，直接添加
            if buffer:  # 之前有积累的短段落，先合并
                buffer += para
                if count_tokens(buffer) >= TARGET_TOKENS:
                    adjusted_chunks.append(buffer)
                    buffer = ""
            else:
                adjusted_chunks.append(para)

    # 最后 buffer 里还有内容的话，作为最后一个 chunk
    if buffer:
        adjusted_chunks.append(buffer)

    return adjusted_chunks

# 示例数据（多个段落）
paragraphs = [
    "Python 是一种高级编程语言，广泛用于数据科学、人工智能、Web 开发等领域。",
    "它的语法简洁，易读易学，并且拥有丰富的第三方库。",
    "在 Python 中，变量是动态类型的，这意味着你可以随时改变变量的值。",
    "例如：你可以先把 x 赋值为整数，然后再将其更改为字符串，而不需要显式声明类型。",
    "Python 还支持多种编程范式，包括面向对象编程、函数式编程和过程式编程。",
    "Python 生态系统非常强大，比如 NumPy、Pandas 用于数据处理，TensorFlow 和 PyTorch 用于深度学习。",
    "对于 Web 开发，Flask 和 Django 提供了高效的框架。",
    "Python 也是自动化脚本、爬虫、DevOps 的首选语言。",
    "由于这些特点，Python 近年来成为最流行的编程语言之一。",
    "本文将详细介绍 Python 的语法、应用场景和最佳实践。" * 5  # 模拟超长段落
]

# 处理段落
processed_chunks = adjust_chunks(paragraphs)

print("\n最终处理后的 chunks:")
for i, chunk in enumerate(processed_chunks):
    print(f"[Chunk {i+1}]: {chunk}\n")
    print(f"长度: {count_tokens(chunk)} tokens\n")
