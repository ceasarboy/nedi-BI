import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.vector_store import VectorStore

def load_schema_docs():
    docs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'schema_business_docs.json')
    with open(docs_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['tables']

def generate_embedding(text: str) -> list:
    import numpy as np
    np.random.seed(hash(text) % (2**32))
    return np.random.rand(384).tolist()

def ingest_docs_to_vector_store():
    print("=" * 60)
    print("开始将Schema业务文档存入向量数据库")
    print("=" * 60)

    tables = load_schema_docs()
    vector_store = VectorStore()

    docs_to_add = []

    for table in tables:
        table_name = table['table_name']
        print(f"\n处理表: {table_name}")

        doc_content = f"""
表名: {table_name}
业务定义: {table['business_definition']}

列信息:
"""

        for col in table['columns']:
            doc_content += f"- {col['name']} ({col['type']}): {col['description']}, 类型: {col.get('dimension_or_measure', 'N/A')}\n"

        doc_content += f"\n外键关系:\n"
        for fk in table.get('foreign_keys', []):
            doc_content += f"- {fk['column']} -> {fk['references']}\n"

        doc_content += f"\n关联路径: {table['relationship_paths']}\n"

        doc_content += f"\n可能的问题:\n"
        for i, q in enumerate(table.get('potential_queries', []), 1):
            doc_content += f"{i}. {q}\n"

        embedding = generate_embedding(table_name)
        docs_to_add.append({
            'id': f"table_{table_name}",
            'content': doc_content,
            'embedding': embedding,
            'metadata': {
                'table_name': table_name,
                'business_definition': table['business_definition'],
                'type': 'table_schema'
            }
        })
        print(f"  ✓ 已生成文档: {table_name}")

    print(f"\n正在添加到向量数据库...")
    ids = [d['id'] for d in docs_to_add]
    embeddings = [d['embedding'] for d in docs_to_add]
    documents = [d['content'] for d in docs_to_add]
    metadatas = [d['metadata'] for d in docs_to_add]

    vector_store.add_vectors(
        collection_name="schema_docs",
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    print(f"\n✓ 成功添加 {len(ids)} 个文档到向量数据库")

    print(f"\n当前集合列表:")
    collections = vector_store.list_collections()
    for col in collections:
        count = vector_store.count(col)
        print(f"  - {col}: {count} 个文档")

    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)

if __name__ == "__main__":
    ingest_docs_to_vector_store()
