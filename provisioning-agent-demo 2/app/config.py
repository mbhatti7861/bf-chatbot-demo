import os

# Tiered models to keep demo cost down:
#   MODEL_ID      — the interactive path (supervisor + read specialists), where routing
#                   accuracy and conflict-synthesis matter → Sonnet 4.5.
#   FAST_MODEL_ID — the pipeline step agents, which are numerous (6 per provision, 3 per
#                   decommission) and tightly scripted → Haiku 4.5.
MODEL_ID      = os.environ.get("BEDROCK_MODEL_ID",      "us.anthropic.claude-sonnet-4-5-20250929-v1:0")
FAST_MODEL_ID = os.environ.get("BEDROCK_FAST_MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")
AWS_REGION    = os.environ.get("AWS_REGION", "us-east-1")

# Document-source retrieval (Knowledge Base + Confluence) embedding model.
# Amazon Titan Text Embeddings V2 supports 256 / 512 / 1024 dimensions and
# server-side normalization, so cosine similarity == inner product.
EMBED_MODEL_ID = os.environ.get("BEDROCK_EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")
EMBED_DIM      = int(os.environ.get("BEDROCK_EMBED_DIM", "1024"))
