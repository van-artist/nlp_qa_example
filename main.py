# type: ignore
from database import DB
from config import DATA_DIR

# Example usage
if __name__ == "__main__":
    client = DB("PKD.db")
    client.create_collection("Tech_", dimension=768)
    client.insert_text("example_collection", ["使用 BERT 模型生成文本的嵌入向量", "接收文本列表，将其转换为向量后插入到指定集合", "支持基于文本的向量搜索"])
    results = client.search("example_collection", "测试", top_k=3)
    print("Search results:", results)