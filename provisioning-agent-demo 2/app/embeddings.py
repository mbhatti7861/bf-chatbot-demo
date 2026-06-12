"""Amazon Titan Text Embeddings V2 via Bedrock.

One text per call (Titan has no batch endpoint); the corpus is small and embedded
once, then cached, so this is not a hot path. Server-side `normalize: true` returns
unit vectors, so downstream cosine similarity is a plain inner product.

Any failure — missing boto3, no AWS creds, no model access, throttling — is raised
as EmbeddingUnavailable so the retrieval layer can fall back to keyword search.
"""
import json
import functools

from .config import AWS_REGION, EMBED_MODEL_ID, EMBED_DIM


class EmbeddingUnavailable(Exception):
    pass


@functools.lru_cache(maxsize=1)
def _client():
    import boto3  # deferred so the app imports even without boto3 installed
    return boto3.client("bedrock-runtime", region_name=AWS_REGION)


def _embed_one(text: str) -> list:
    body = json.dumps({"inputText": text[:8000], "dimensions": EMBED_DIM, "normalize": True})
    resp = _client().invoke_model(modelId=EMBED_MODEL_ID, body=body)
    return json.loads(resp["body"].read())["embedding"]


def embed(texts: list) -> list:
    """Embed a list of strings → list of normalized vectors. Raises EmbeddingUnavailable."""
    try:
        return [_embed_one(t) for t in texts]
    except Exception as e:
        raise EmbeddingUnavailable(str(e))
