import os 

from bert_score import score
from transformers import AutoModel, AutoTokenizer

from backend.app.agents.base_agent import BaseAgent
from backend.app.config.config import Config
from backend.app.utils.debate import *

class EvaluationAgent(BaseAgent):
    def __init__(self):
      # Check if the model exists locally
      if Config.DEBERTA_LARGE_MODEL_PATH.exists():
          print(f"Loading model from local path: {Config.DEBERTA_LARGE_MODEL_PATH}", flush = True)
      else:
          print(f"Local path not found. Downloading model: {DEBERTA_MODEL_NAME}", flush = True)

          os.makedirs(str(Config.DEBERTA_LARGE_MODEL_PATH), exist_ok=True)

          tokenizer = AutoTokenizer.from_pretrained(DEBERTA_MODEL_NAME)
          model = AutoModel.from_pretrained(DEBERTA_MODEL_NAME)

          model.save_pretrained(str(Config.DEBERTA_LARGE_MODEL_PATH))
          tokenizer.save_pretrained(str(Config.DEBERTA_LARGE_MODEL_PATH))

      self.model_name = Config.DEBERTA_LARGE_MODEL_PATH

    def evaluate(self, allam_output, gpt_output):
      reference = [gpt_output]
      candidate = [allam_output]

      (P, R, F), hashname = score(candidate, reference, model_type = self.model_name, return_hash = True)

      return P.mean().item(), R.mean().item(), F.mean().item()