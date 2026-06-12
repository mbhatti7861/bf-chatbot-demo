"""Vector retrieval for the document sources (Knowledge Base, Confluence).

  Embeddings : Amazon Titan Text Embeddings V2 (Bedrock) — see embeddings.py
  Index      : in-process FAISS IndexFlatIP over normalized vectors (cosine).
               FAISS is optional; if it is not installed we fall back to a NumPy
               matrix dot-product, which is identical math for a corpus this size.
  Cache      : corpus embeddings are persisted to data/.embeddings_cache.json,
               keyed by a signature of (embedding model + corpus content), so we
               embed the corpus once — not on every server start.
  Fallback   : if embeddings are unavailable (no creds / no model access) or NumPy
               is missing, retrieval transparently falls back to keyword overlap so
               the demo always runs. BACKEND reflects which path is live.

ServiceNow and Jira do NOT come through here — structured records stay exact
lookups and are never embedded.
"""
import json
import hashlib
import pathlib

from .config import EMBED_MODEL_ID
from . import embeddings

_CACHE = pathlib.Path(__file__).resolve().parent.parent / "data" / ".embeddings_cache.json"

# "vector" once at least one index embeds successfully; "keyword" if we fell back.
BACKEND = "pending"


def _cite(d: dict, source: str) -> dict:
    return {"citation": f"{source} · {d.get('space', source)}/{d['id']}",
            "title": d["title"], "snippet": d["text"][:320]}


def _keyword(docs: list, query: str, source: str, top: int) -> list:
    terms = [t for t in query.lower().replace("/", " ").split() if len(t) > 2]
    hits = []
    for d in docs:
        hay   = (d["title"] + " " + d["text"]).lower()
        score = sum(1 for t in terms if t in hay)
        if score:
            hits.append((score, d))
    hits.sort(key=lambda x: -x[0])
    return [_cite(d, source) for _, d in hits[:top]]


def _doc_text(d: dict) -> str:
    return f"{d['title']} — {d['text']}"


def _signature(docs: list) -> str:
    h = hashlib.sha256()
    h.update(EMBED_MODEL_ID.encode())
    for d in docs:
        h.update(d["id"].encode())
        h.update(_doc_text(d).encode())
    return h.hexdigest()


def _load_cache() -> dict:
    try:
        return json.loads(_CACHE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_cache(cache: dict):
    try:
        _CACHE.write_text(json.dumps(cache), encoding="utf-8")
    except Exception:
        pass


class Index:
    """Lazily-built vector index for one document corpus, with keyword fallback."""

    def __init__(self, name: str, docs: list, source: str):
        self.name   = name
        self.docs   = docs
        self.source = source
        self.mode   = None          # "vector" | "keyword"
        self._built = False
        self._np    = None
        self._mat   = None          # NumPy (n, dim) normalized matrix
        self._faiss = None          # optional FAISS index

    def build(self):
        global BACKEND
        if self._built:
            return
        vectors = self._corpus_vectors()
        if vectors is not None:
            try:
                import numpy as np
                self._np  = np
                self._mat = np.asarray(vectors, dtype="float32")
                try:
                    import faiss
                    idx = faiss.IndexFlatIP(self._mat.shape[1])
                    idx.add(self._mat)
                    self._faiss = idx
                except Exception:
                    self._faiss = None      # NumPy path; same result
                self.mode = "vector"
            except Exception:
                self.mode = "keyword"       # NumPy missing
        else:
            self.mode = "keyword"           # embeddings unavailable
        self._built = True
        BACKEND = self.mode if BACKEND in ("pending", self.mode) else "keyword"

    def _corpus_vectors(self):
        """Embed the corpus, using the on-disk cache when the corpus is unchanged."""
        sig   = _signature(self.docs)
        cache = _load_cache()
        if cache.get(self.name, {}).get("sig") == sig:
            return cache[self.name]["vectors"]
        try:
            vectors = embeddings.embed([_doc_text(d) for d in self.docs])
        except embeddings.EmbeddingUnavailable:
            return None
        cache[self.name] = {"sig": sig, "vectors": vectors}
        _save_cache(cache)
        return vectors

    def search(self, query: str, top: int = 4) -> list:
        self.build()
        if self.mode == "vector":
            try:
                qv = self._np.asarray(embeddings.embed([query]), dtype="float32")  # 1 Titan call
                k  = min(top, len(self.docs))
                if self._faiss is not None:
                    _, idxs = self._faiss.search(qv, k)
                    order = [i for i in idxs[0] if i >= 0]
                else:
                    sims  = self._mat @ qv[0]
                    order = list(self._np.argsort(-sims)[:k])
                return [_cite(self.docs[int(i)], self.source) for i in order]
            except embeddings.EmbeddingUnavailable:
                pass  # creds lost mid-session → answer this query via keyword
        return _keyword(self.docs, query, self.source, top)
