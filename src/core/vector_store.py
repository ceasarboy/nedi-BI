import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import os
from pathlib import Path

class VectorStore:
    def __init__(self, persist_directory: str = None):
        if persist_directory is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            persist_directory = str(base_dir / "config" / "vector_data")

        os.makedirs(persist_directory, exist_ok=True)

        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collections = {}

    def get_or_create_collection(self, name: str, metadata: Dict = None) -> chromadb.Collection:
        if name not in self.collections:
            self.collections[name] = self.client.get_or_create_collection(
                name=name,
                metadata=metadata or {"description": f"Collection: {name}"}
            )
        return self.collections[name]

    def add_vectors(
        self,
        collection_name: str,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str] = None,
        metadatas: List[Dict] = None
    ) -> bool:
        try:
            collection = self.get_or_create_collection(collection_name)
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            return True
        except Exception as e:
            print(f"Error adding vectors: {e}")
            return False

    def query(
        self,
        collection_name: str,
        query_embeddings: List[List[float]],
        n_results: int = 10,
        where: Dict = None,
        where_document: Dict = None
    ) -> Dict[str, Any]:
        try:
            collection = self.get_or_create_collection(collection_name)
            results = collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where,
                where_document=where_document
            )
            return {
                "success": True,
                "ids": results.get("ids", []),
                "distances": results.get("distances", []),
                "metadatas": results.get("metadatas", []),
                "documents": results.get("documents", [])
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_by_id(self, collection_name: str, ids: List[str]) -> Dict[str, Any]:
        try:
            collection = self.get_or_create_collection(collection_name)
            results = collection.get(ids=ids)
            return {
                "success": True,
                "ids": results.get("ids", []),
                "metadatas": results.get("metadatas", []),
                "documents": results.get("documents", [])
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def delete_collection(self, collection_name: str) -> bool:
        try:
            self.client.delete_collection(name=collection_name)
            if collection_name in self.collections:
                del self.collections[collection_name]
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False

    def list_collections(self) -> List[str]:
        try:
            return [col.name for col in self.client.list_collections()]
        except Exception as e:
            print(f"Error listing collections: {e}")
            return []

    def count(self, collection_name: str) -> int:
        try:
            collection = self.get_or_create_collection(collection_name)
            return collection.count()
        except Exception as e:
            print(f"Error counting: {e}")
            return 0


vector_store = VectorStore()

def get_vector_store() -> VectorStore:
    return vector_store
