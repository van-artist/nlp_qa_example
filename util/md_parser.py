import os
import json
import re
from typing import List, Dict, Any,Optional
from dataclasses import dataclass, field
from .chunking import split_long_text, adjust_chunks

@dataclass
class MarkdownBlock:
    """
    Markdown 解析后的层级结构，包含：
    - title: 标题名称
    - content: 该标题下的正文
    - children: 子标题列表
    """
    title: Optional[str]  
    content: str = ""  
    children: List["MarkdownBlock"] = field(default_factory=list)  

def parse_markdown(file_path: str) -> List[MarkdownBlock]:
    """
    解析 Markdown 文件，构建嵌套的标题层次结构，并对 content 进行 chunk 处理。

    :param file_path: Markdown 文件路径
    :return: 解析后的标题层级结构，返回 MarkdownBlock 对象列表
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")

    root = MarkdownBlock(title=None)  
    stack = [root] 
    last_node = root 
    current_content: List[str] = [] 

    for line in lines:
        line = line.strip()
        if not line:
            continue  

        header_match = re.match(r"^(#{1,6})\s+(.+)", line)

        if header_match:
            if current_content and last_node:
                last_node.content += ''.join(adjust_chunks(current_content))  
                current_content = [] 
            
            level = len(header_match.group(1))  
            title = header_match.group(2).strip()

            new_node = MarkdownBlock(title=title)

            while len(stack) > level:
                stack.pop()
            stack[-1].children.append(new_node)
            stack.append(new_node)
            last_node = new_node  
        else:
            current_content.append(line)

    if current_content and last_node:
        last_node.content += ''.join(adjust_chunks(current_content))

    return root.children  

def traverse_markdown_files_by_tree(root_dir):
    """
    遍历目录，解析所有 Markdown 文件，并构建 JSON
    """
    md_data = []
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)

                md_blocks = parse_markdown(file_path)

                relative_path = os.path.relpath(file_path, root_dir)
                for md_block in md_blocks:
                    md_data.append({
                        "file": relative_path,
                        "title": md_block.title,
                        "content": md_block.content
                    })

    return md_data
