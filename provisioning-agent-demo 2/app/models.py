from strands.models import BedrockModel

from .config import MODEL_ID

MODEL = BedrockModel(model_id=MODEL_ID, temperature=0.2, streaming=False)
