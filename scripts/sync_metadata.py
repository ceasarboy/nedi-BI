import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from src.core.vector_store import VectorStore

def get_table_names(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

def get_table_schema(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    conn.close()
    return columns

def get_sample_data(db_path, table_name, limit=3):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
    rows = cursor.fetchall()
    conn.close()
    return rows

def generate_embedding(text: str) -> list:
    import numpy as np
    np.random.seed(hash(text) % (2**32))
    return np.random.rand(384).tolist()

def sync_metadata():
    print("=" * 60)
    print("元数据同步脚本")
    print("=" * 60)

    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'pb_bi.db')
    print(f"\n数据库路径: {db_path}")
    print(f"数据库存在: {os.path.exists(db_path)}")

    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在: {db_path}")
        return

    vector_store = VectorStore()

    table_names = get_table_names(db_path)
    print(f"\n发现 {len(table_names)} 个表: {table_names}")

    total_docs = 0

    for table_name in table_names:
        print(f"\n处理表: {table_name}")

        columns = get_table_schema(db_path, table_name)
        column_names = [col[1] for col in columns]
        column_types = {col[1]: col[2] for col in columns}

        print(f"  列: {column_names}")

        markdown_content = f"""# 表: {table_name}

## Schema 信息

| 列名 | 类型 | 可空 | 主键 |
|------|------|------|------|
"""
        for col in columns:
            col_name, col_type, not_null, default_val, is_pk = col[1], col[2], col[3], col[4], col[5]
            markdown_content += f"| {col_name} | {col_type} | {'否' if not_null else '是'} | {'是' if is_pk else '否'} |\n"

        sample_data = get_sample_data(db_path, table_name, limit=3)
        if sample_data:
            markdown_content += f"\n## 样本数据 (前 {len(sample_data)} 条)\n\n"
            markdown_content += "| " + " | ".join(column_names) + " |\n"
            markdown_content += "| " + " | ".join(["---"] * len(column_names)) + " |\n"

            for row in sample_data:
                row_values = [str(v) if v is not None else "NULL" for v in row]
                markdown_content += "| " + " | ".join(row_values) + " |\n"

            for col_idx, col_name in enumerate(column_names):
                sample_values = list(set([str(row[col_idx]) for row in sample_data if row[col_idx] is not None]))[:3]

                col_embedding = generate_embedding(f"{table_name}.{col_name}")
                col_content = f"""表: {table_name}
列: {col_name}
类型: {column_types.get(col_name, 'unknown')}
样本值: {', '.join(sample_values) if sample_values else 'N/A'}"""

                col_metadata = {
                    "table_name": table_name,
                    "column_name": col_name,
                    "data_type": column_types.get(col_name, "unknown"),
                    "type": "column"
                }

                doc_id = f"{table_name}_{col_name}"
                vector_store.add_vectors(
                    collection_name="metadata",
                    ids=[doc_id],
                    embeddings=[col_embedding],
                    documents=[col_content],
                    metadatas=[col_metadata]
                )
                total_docs += 1
                print(f"    ✓ 添加列元数据: {col_name}")

        table_embedding = generate_embedding(table_name)
        table_content = f"""表: {table_name}
列数: {len(columns)}
列名: {', '.join(column_names)}"""

        table_metadata = {
            "table_name": table_name,
            "column_name": "*",
            "data_type": "table",
            "type": "table"
        }

        vector_store.add_vectors(
            collection_name="metadata",
            ids=[table_name],
            embeddings=[table_embedding],
            documents=[markdown_content],
            metadatas=[table_metadata]
        )
        total_docs += 1
        print(f"    ✓ 添加表元数据: {table_name}")

    print("\n" + "=" * 60)
    print(f"元数据同步完成!")
    print(f"总计添加 {total_docs} 个文档")
    print("=" * 60)

    print(f"\n当前集合列表:")
    collections = vector_store.list_collections()
    for col in collections:
        count = vector_store.count(col)
        print(f"  - {col}: {count} 个文档")

if __name__ == "__main__":
    sync_metadata()
