import chromadb
import uuid
import numpy as np
from typing import List
from ..providers.base import AbstractEmbedProvider
from ..config import settings
from ..models.schemas import MergedData

def get_chroma_client():
    return chromadb.Client()

async def deduplicate_observations(observations: List[str], embed_provider: AbstractEmbedProvider, job_id: str) -> List[str]:
    if not observations:
        return []
        
    client = get_chroma_client()
    # chromadb collection names must not contain hyphens if they aren't matching strict rules
    collection_name = f"obs_{job_id.replace('-', '')}"
    
    try:
        collection = client.create_collection(name=collection_name)
    except Exception:
        collection = client.get_collection(name=collection_name)

    # 1. Embed all in a single batch call
    embeddings = await embed_provider.embed_texts(observations)

    # Add to chroma
    ids = [str(uuid.uuid4()) for _ in observations]
    collection.add(
        embeddings=embeddings,
        documents=observations,
        ids=ids
    )

    keep_indices = set(range(len(observations)))
    
    arr = np.array(embeddings)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms[norms == 0] = 1
    normalized_arr = arr / norms
    similarity_matrix = np.dot(normalized_arr, normalized_arr.T)

    for i in range(len(observations)):
        if i not in keep_indices:
            continue
        for j in range(i + 1, len(observations)):
            if j not in keep_indices:
                continue
            
            sim = similarity_matrix[i][j]
            if sim > settings.dedup_similarity_threshold:
                if len(observations[i]) >= len(observations[j]):
                    keep_indices.remove(j)
                else:
                    keep_indices.remove(i)
                    break

    deduped = [observations[i] for i in sorted(keep_indices)]
    
    try:
        client.delete_collection(name=collection_name)
    except Exception:
        pass
        
    return deduped

def collect_all_observations(merged: MergedData) -> List[str]:
    obs = []
    for area in merged.areas:
        obs.extend(area.negative_observations)
        obs.extend(area.positive_observations)
    return list(set(obs))

def apply_deduped_observations(merged: MergedData, deduped_obs: List[str]) -> MergedData:
    valid_set = set(deduped_obs)
    for area in merged.areas:
        area.negative_observations = [o for o in area.negative_observations if o in valid_set]
        area.positive_observations = [o for o in area.positive_observations if o in valid_set]
    return merged
