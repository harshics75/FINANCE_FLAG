"""Vector store abstraction: Azure AI Search (preferred) or local FAISS fallback."""
import json
import os
import threading
from abc import ABC, abstractmethod

import numpy as np

from app.config.settings import get_settings

settings = get_settings()


class VectorStore(ABC):
    @abstractmethod
    def upsert(self, ids: list[str], vectors: list[list[float]], payloads: list[dict]) -> None: ...

    @abstractmethod
    def search(self, vector: list[float], k: int = 8, filters: dict | None = None) -> list[dict]: ...


class FaissStore(VectorStore):
    """Local FAISS index persisted to disk; payloads stored in a sidecar JSON file."""

    def __init__(self, dim: int = 3072, path: str = "/data/uploads/faiss"):
        import faiss
        self._faiss = faiss
        self.dim = dim
        self.path = path
        self.lock = threading.Lock()
        os.makedirs(path, exist_ok=True)
        self.index_file = os.path.join(path, "index.bin")
        self.meta_file = os.path.join(path, "meta.json")
        if os.path.exists(self.index_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.meta_file) as f:
                self.meta: list[dict] = json.load(f)
        else:
            self.index = faiss.IndexFlatIP(dim)
            self.meta = []

    def upsert(self, ids, vectors, payloads):
        with self.lock:
            arr = np.array(vectors, dtype="float32")
            arr /= (np.linalg.norm(arr, axis=1, keepdims=True) + 1e-9)
            self.index.add(arr)
            for i, pid in enumerate(ids):
                self.meta.append({"id": pid, **payloads[i]})
            self._faiss.write_index(self.index, self.index_file)
            with open(self.meta_file, "w") as f:
                json.dump(self.meta, f)

    def search(self, vector, k=8, filters=None):
        if self.index.ntotal == 0:
            return []
        q = np.array([vector], dtype="float32")
        q /= (np.linalg.norm(q) + 1e-9)
        scores, idxs = self.index.search(q, min(k * 3, self.index.ntotal))
        results = []
        for score, idx in zip(scores[0], idxs[0]):
            if idx < 0:
                continue
            item = self.meta[idx]
            if filters and any(item.get(fk) != fv for fk, fv in filters.items()):
                continue
            results.append({**item, "score": float(score)})
            if len(results) >= k:
                break
        return results


class AzureSearchStore(VectorStore):
    def __init__(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.search.documents import SearchClient
        self.client = SearchClient(settings.azure_search_endpoint, settings.azure_search_index,
                                   AzureKeyCredential(settings.azure_search_api_key))

    def upsert(self, ids, vectors, payloads):
        docs = [{"id": pid, "vector": vec, **payload}
                for pid, vec, payload in zip(ids, vectors, payloads)]
        self.client.upload_documents(docs)

    def search(self, vector, k=8, filters=None):
        from azure.search.documents.models import VectorizedQuery
        vq = VectorizedQuery(vector=vector, k_nearest_neighbors=k, fields="vector")
        flt = " and ".join(f"{fk} eq '{fv}'" for fk, fv in (filters or {}).items()) or None
        results = self.client.search(search_text=None, vector_queries=[vq], filter=flt, top=k)
        return [{**dict(r), "score": r["@search.score"]} for r in results]


_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    global _store
    if _store is None:
        _store = AzureSearchStore() if settings.vector_store == "azure_search" else FaissStore()
    return _store
