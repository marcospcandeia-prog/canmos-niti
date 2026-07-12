import logging
from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_ollama import OllamaEmbeddings

from app.core.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_client: Optional[QdrantClient] = None
_embeddings: Optional[OllamaEmbeddings] = None

VECTOR_SIZE = 768
COLLECTION_NAME = settings.QDRANT_COLLECTION


def get_qdrant_client() -> Optional[QdrantClient]:
    global _client
    if _client is None:
        try:
            _client = QdrantClient(url=settings.QDRANT_HOST)
            logger.info(f"Qdrant client connected: {settings.QDRANT_HOST}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            _client = None
    return _client


def get_embeddings_client() -> Optional[OllamaEmbeddings]:
    global _embeddings
    if _embeddings is None:
        try:
            _embeddings = OllamaEmbeddings(
                model=settings.OLLAMA_MODEL,
                base_url=settings.OLLAMA_HOST,
            )
            logger.info("Embeddings client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            _embeddings = None
    return _embeddings


def ensure_collection() -> bool:
    client = get_qdrant_client()
    if not client:
        return False
    
    try:
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if COLLECTION_NAME not in collection_names:
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )
            logger.info(f"Created Qdrant collection: {COLLECTION_NAME}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to ensure Qdrant collection: {e}")
        return False


def index_document(
    document_id: int,
    user_id: int,
    text: str,
    metadata: Optional[dict] = None,
) -> bool:
    client = get_qdrant_client()
    embeddings = get_embeddings_client()
    
    if not client or not embeddings:
        logger.warning("Qdrant or embeddings not available, skipping indexing")
        return False
    
    try:
        ensure_collection()
        
        chunks = _chunk_text(text, chunk_size=500, overlap=50)
        
        points = []
        for i, chunk in enumerate(chunks):
            vector = embeddings.embed_query(chunk)
            
            point = PointStruct(
                id=document_id * 1000 + i,
                vector=vector,
                payload={
                    "document_id": document_id,
                    "user_id": user_id,
                    "chunk_index": i,
                    "text": chunk,
                    "metadata": metadata or {},
                },
            )
            points.append(point)
        
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        logger.info(f"Indexed {len(chunks)} chunks for document {document_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to index document {document_id}: {e}")
        return False


def search_similar(
    query: str,
    user_id: int,
    limit: int = 3,
) -> list[dict]:
    client = get_qdrant_client()
    embeddings = get_embeddings_client()
    
    if not client or not embeddings:
        logger.warning("Qdrant or embeddings not available, skipping search")
        return []
    
    try:
        query_vector = embeddings.embed_query(query)
        
        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit,
            query_filter={
                "must": [
                    {"key": "user_id", "match": {"value": user_id}}
                ]
            },
        )
        
        sources = []
        for hit in results:
            payload = hit.payload
            sources.append({
                "document_id": payload.get("document_id"),
                "text": payload.get("text", "")[:200],
                "score": hit.score,
            })
        
        logger.info(f"Found {len(sources)} similar chunks for query")
        return sources
    except Exception as e:
        logger.error(f"Failed to search similar: {e}")
        return []


def delete_document_vectors(document_id: int) -> bool:
    client = get_qdrant_client()
    if not client:
        return False
    
    try:
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector={
                "filter": {
                    "must": [
                        {"key": "document_id", "match": {"value": document_id}}
                    ]
                }
            },
        )
        logger.info(f"Deleted vectors for document {document_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete vectors for document {document_id}: {e}")
        return False


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    
    return chunks
