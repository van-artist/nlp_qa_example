# type:ignore
import os
import torch
from transformers import AutoTokenizer, AutoModel
from pymilvus import MilvusClient, CollectionSchema, FieldSchema, DataType

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

class DB:
    def __init__(self, name: str, model_name: str = "bert-base-chinese"):
        """
        初始化数据库客户端并连接到 Milvus。
        同时加载用于文本嵌入的分词器和模型。

        :param name: Milvus 数据库名称。
        :param model_name: HuggingFace 预训练模型名称，用于生成文本嵌入。
        """
        self.name = name
        self.client = MilvusClient()
        print(f"已连接到 Milvus 数据库: {self.name}")
        
        # 加载分词器和模型
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()  # 设置模型为推理模式
        print(f"已加载嵌入模型: {model_name}")

    def create_collection(self, collection_name: str, dimension: int = 768):
        """
        在 Milvus 中创建一个向量集合（collection），用于存储向量数据。
        如果集合已存在，则会先删除并重新创建。

        :param collection_name: 要创建的集合名称。
        :param dimension: 向量的维度，默认为 768。
        """
        if self.client.has_collection(collection_name=collection_name):
            print(f"集合 {collection_name} 已存在，正在删除并重新创建...")
            self.client.drop_collection(collection_name=collection_name)

        schema = CollectionSchema(
            fields=[
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dimension)
            ],
            description=f"{collection_name} 的向量存储"
        )
        self.client.create_collection(name=collection_name, schema=schema)
        print(f"集合 {collection_name} 创建成功，维度为 {dimension}。")

    def embed_text(self, text: str) -> list:
        """
        使用预训练模型将文本转换为向量嵌入。

        :param text: 输入文本。
        :return: 文本的嵌入向量（列表格式）。
        """
        # 分词并转换为张量
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # 取 [CLS] 位置的向量作为文本嵌入
        embedding = outputs.last_hidden_state[:, 0, :].squeeze().tolist()
        print(f"已为文本生成嵌入: {text}")
        return embedding

    def insert_text(self, collection_name: str, texts: list):
        """
        将一批文本转换为嵌入向量，并存入指定的集合。

        :param collection_name: 存储数据的集合名称。
        :param texts: 待转换并插入的文本列表。
        """
        if not self.client.has_collection(collection_name=collection_name):
            raise ValueError(f"集合 {collection_name} 不存在。")

        # 生成所有文本的嵌入
        embeddings = [self.embed_text(text) for text in texts]
        
        # 插入嵌入向量到 Milvus
        ids = self.client.insert(collection_name=collection_name, data={"vector": embeddings})
        print(f"已向集合 {collection_name} 插入 {len(texts)} 条文本数据。")
        return ids

    def search(self, collection_name: str, query_text: str, top_k: int):
        """
        在指定的集合中搜索与输入文本最相似的 top_k 条记录。

        :param collection_name: 需要搜索的集合名称。
        :param query_text: 查询的文本，系统会将其转换为嵌入向量进行搜索。
        :param top_k: 返回的相似度最高的结果数。
        :return: 搜索结果。
        """
        query_vector = self.embed_text(query_text)
        results = self.client.search(
            collection_name=collection_name,
            data={"vector": [query_vector]},
            top_k=top_k
        )
        print(f"在 {collection_name} 中搜索完成，返回 {len(results)} 条结果。")
        return results

    def drop_collection(self, collection_name: str):
        """
        删除指定的集合（collection）。

        :param collection_name: 要删除的集合名称。
        """
        if self.client.has_collection(collection_name=collection_name):
            self.client.drop_collection(collection_name=collection_name)
            print(f"集合 {collection_name} 已删除。")

