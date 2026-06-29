import os

# Tiered models to keep demo cost down:
#   MODEL_ID      — the interactive path (supervisor + read specialists), where routing
#                   accuracy and conflict-synthesis matter → Sonnet 4.5.
#   FAST_MODEL_ID — the pipeline step agents, which are numerous (6 per provision, 3 per
#                   decommission) and tightly scripted → Haiku 4.5.
MODEL_ID      = os.environ.get("BEDROCK_MODEL_ID",      "us.anthropic.claude-sonnet-4-5-20250929-v1:0")
FAST_MODEL_ID = os.environ.get("BEDROCK_FAST_MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")
AWS_REGION    = os.environ.get("AWS_REGION", "us-east-1")


def model_label(model_id: str) -> str:
    """Short friendly label (e.g. 'Sonnet 4.5') for display in the UI."""
    import re
    m   = model_id.lower()
    fam = ("Sonnet" if "sonnet" in m else "Haiku" if "haiku" in m
           else "Opus" if "opus" in m else "Claude")
    mt  = re.search(r"(?:sonnet|haiku|opus)-(\d)-(\d)", m)
    ver = f"{mt.group(1)}.{mt.group(2)}" if mt else ""
    return f"{fam} {ver}".strip()


MODEL_LABEL      = model_label(MODEL_ID)       # interactive path (Sonnet)
FAST_MODEL_LABEL = model_label(FAST_MODEL_ID)  # pipeline steps (Haiku)

# Document-source retrieval (Knowledge Base + Confluence) embedding model.
# Amazon Titan Text Embeddings V2 supports 256 / 512 / 1024 dimensions and
# server-side normalization, so cosine similarity == inner product.
EMBED_MODEL_ID = os.environ.get("BEDROCK_EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")
EMBED_DIM      = int(os.environ.get("BEDROCK_EMBED_DIM", "1024"))
