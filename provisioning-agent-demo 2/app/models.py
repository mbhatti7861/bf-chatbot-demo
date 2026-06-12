from strands.models import BedrockModel

from .config import MODEL_ID, FAST_MODEL_ID

# MODEL      — interactive path (supervisor + read specialists): Sonnet 4.5
# FAST_MODEL — pipeline step agents: Haiku 4.5 (cheaper, plenty for scripted steps)
MODEL      = BedrockModel(model_id=MODEL_ID,      temperature=0.2, streaming=False)
FAST_MODEL = BedrockModel(model_id=FAST_MODEL_ID, temperature=0.2, streaming=False)
