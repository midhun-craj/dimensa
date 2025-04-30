import chromadb
from sentence_transformers import SentenceTransformer
from typing import List
from datetime import datetime
from uuid import uuid4

_model = None
_collection = None
_collection_name = "memory_collections"

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def get_collection():
    global _collection
    if _collection is None:
        client = chromadb.HttpClient(host="chromadb", port=8083)
        existing_collections = client.list_collections()
        collection_names = [col.name for col in existing_collections]

        if _collection_name not in collection_names:
            _collection =client.create_collection(_collection_name)
        else:
            _collection = client.get_collection(_collection_name)
    
    return _collection

def save_to_long_term_memory(session_id: str, user_prompt: str, assistant_response: str):
    model = get_model()
    collection = get_collection()

    full_memory = user_prompt + " " + assistant_response
    embedding = model.encode(full_memory)

    metadata = {
        'session_id': session_id,
        'timestamp': datetime.now().isoformat(),
        'user_prompt': user_prompt,
        'assistant_response': assistant_response
    }

    collection.add(
        ids=[str(uuid4())],
        documents=[full_memory],
        metadatas=[metadata],
        embeddings=[embedding]
    )

def get_long_term_memory(session_id: str, user_query: str, top_k: int = 3) -> List[dict]:
    model = get_model()
    collection = get_collection()

    query_embedding = model.encode(user_query)

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k * 2
    )

    result_memories = []
    for metadata in results.get("metadatas", [])[0]:
        if metadata.get("session_id") == session_id:
            result_memories.append(metadata)
        if len(result_memories) >= top_k:
            break

    return result_memories