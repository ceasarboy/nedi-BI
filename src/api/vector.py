from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import numpy as np

from src.core.vector_store import get_vector_store, VectorStore
from src.core.permissions import get_current_user

router = APIRouter(prefix="/api/vector", tags=["vector"])

class VectorAddRequest(BaseModel):
    collection_name: str
    ids: List[str]
    embeddings: List[List[float]]
    documents: List[str] = []
    metadatas: List[Dict[str, Any]] = []

class VectorQueryRequest(BaseModel):
    collection_name: str
    query_embedding: List[float]
    n_results: int = 10
    filter_dict: Optional[Dict[str, Any]] = None

class VectorConvertRequest(BaseModel):
    texts: List[str]
    model: str = "sentence-transformers/all-MiniLM-L6-v2"

def text_to_embedding(text: str, model: str = "sentence-transformers/all-MiniLM-L6-v2") -> List[float]:
    try:
        from sentence_transformers import SentenceTransformer
        model_instance = SentenceTransformer(model)
        embedding = model_instance.encode(text)
        return embedding.tolist()
    except ImportError:
        np.random.seed(hash(text) % (2**32))
        return np.random.rand(384).tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成embedding失败: {str(e)}")

@router.post("/embeddings")
async def create_embeddings(
    request: VectorConvertRequest,
    current_user = Depends(get_current_user)
):
    try:
        embeddings = [text_to_embedding(text, request.model) for text in request.texts]
        return {
            "success": True,
            "embeddings": embeddings,
            "count": len(embeddings)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add")
async def add_vectors(
    request: VectorAddRequest,
    vector_store: VectorStore = Depends(get_vector_store),
    current_user = Depends(get_current_user)
):
    success = vector_store.add_vectors(
        collection_name=request.collection_name,
        ids=request.ids,
        embeddings=request.embeddings,
        documents=request.documents,
        metadatas=request.metadatas
    )

    if success:
        return {"success": True, "message": f"成功添加 {len(request.ids)} 个向量到集合 {request.collection_name}"}
    else:
        raise HTTPException(status_code=500, detail="添加向量失败")

@router.post("/query")
async def query_vectors(
    request: VectorQueryRequest,
    vector_store: VectorStore = Depends(get_vector_store),
    current_user = Depends(get_current_user)
):
    result = vector_store.query(
        collection_name=request.collection_name,
        query_embeddings=[request.query_embedding],
        n_results=request.n_results,
        where=request.filter_dict
    )

    if result.get("success"):
        return result
    else:
        raise HTTPException(status_code=500, detail=result.get("error", "查询失败"))

@router.get("/collections")
async def list_collections(
    vector_store: VectorStore = Depends(get_vector_store),
    current_user = Depends(get_current_user)
):
    collections = vector_store.list_collections()
    collection_info = []
    for name in collections:
        count = vector_store.count(name)
        collection_info.append({"name": name, "count": count})

    return {
        "success": True,
        "collections": collection_info
    }

@router.delete("/collections/{collection_name}")
async def delete_collection(
    collection_name: str,
    vector_store: VectorStore = Depends(get_vector_store),
    current_user = Depends(get_current_user)
):
    success = vector_store.delete_collection(collection_name)
    if success:
        return {"success": True, "message": f"集合 {collection_name} 已删除"}
    else:
        raise HTTPException(status_code=500, detail="删除集合失败")

@router.get("/collections/{collection_name}/count")
async def get_collection_count(
    collection_name: str,
    vector_store: VectorStore = Depends(get_vector_store),
    current_user = Depends(get_current_user)
):
    count = vector_store.count(collection_name)
    return {"success": True, "collection_name": collection_name, "count": count}
