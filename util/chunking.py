import re
from typing import List
from config import MAX_TOKENS, MIN_TOKENS, TARGET_TOKENS


def tokenize(text: str) -> List[str]:
    """ 
    将文本 token 化，假设每个汉字是一个 token，英文单词按空格分词。
    """
    return list(text) 


def count_tokens(text: str) -> int:
    """ 计算文本的 token 数量 """
    return len(tokenize(text))


def split_long_text(text: str, max_length: int = MAX_TOKENS) -> List[str]:
    """
    如果文本过长，按照标点符号（句号、感叹号、问号、换行）拆分，确保每个 chunk <= max_length
    - 尽可能保持上下文完整
    - 如果拆分后仍然过长，继续拆分
    """
    sentences = re.split(r'(。|！|？|\n)', text)  
    chunks, current_chunk = [], ""

    for sentence in sentences:
        if not sentence.strip(): 
            continue

        if count_tokens(current_chunk + sentence) > max_length:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence
        else:
            current_chunk += sentence

    if current_chunk:  
        chunks.append(current_chunk)

    return chunks


def adjust_chunks(paragraphs: List[str]) -> List[str]:
    """
    遍历原始段落列表，进行：
    1. 过长的段落拆分
    2. 过短的段落合并
    3. 目标 chunk 维持在 TARGET_TOKENS 以内

    :param paragraphs: 原始文本段落列表
    :return: 经过处理后的 chunk 列表
    """
    adjusted_chunks = []
    buffer = ""

    for para in paragraphs:
        para_tokens = count_tokens(para)

        if para_tokens > MAX_TOKENS:
            adjusted_chunks.extend(split_long_text(para, MAX_TOKENS))
        elif para_tokens < MIN_TOKENS:
            buffer += para
            if count_tokens(buffer) >= MIN_TOKENS:
                adjusted_chunks.append(buffer)
                buffer = ""
        else:
            if buffer: 
                buffer += para
                if count_tokens(buffer) >= TARGET_TOKENS:
                    adjusted_chunks.append(buffer)
                    buffer = ""
            else:
                adjusted_chunks.append(para)

    if buffer:
        adjusted_chunks.append(buffer)

    return adjusted_chunks


__all__ = ["tokenize", "count_tokens", "split_long_text", "adjust_chunks"]
