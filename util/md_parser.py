import os
import json
import re

def parse_markdown(file_path):
    """
    解析 Markdown 文件，构建嵌套的标题层次结构
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    root = {"title": None, "content": "", "children": []}
    stack = [root]

    for line in lines:
        header_match = re.match(r"^(#{1,6})\s+(.+)", line)
        if header_match:
            level = len(header_match.group(1))  # 标题层级
            title = header_match.group(2).strip()

            # 创建新节点
            new_node = {"title": title, "content": "", "children": []}

            # 维护层级栈
            while len(stack) > level:  # 回溯到正确的父级
                stack.pop()
            stack[-1]["children"].append(new_node)
            stack.append(new_node)  # 更新当前层级
        else:
            # 处理正文内容
            stack[-1]["content"] += line + " "

    return root["children"]  # 返回去掉根节点的内容

def traverse_markdown_files_by_tree(root_dir):
    """
    遍历目录，解析所有 Markdown 文件，并构建 JSON
    """
    md_data = []
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)

                # 解析 Markdown 结构
                md_structure = parse_markdown(file_path)

                # 组织 JSON 数据
                relative_path = os.path.relpath(file_path, root_dir)
                md_data.append({
                    "path": relative_path,
                    "structure": md_structure
                })

    return md_data
