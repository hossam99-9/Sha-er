import os 

from bert_score import score
from transformers import AutoModel, AutoTokenizer

from backend.app.agents.base_agent import BaseAgent
from backend.app.config.config import Config
from backend.app.utils.debate import *

class EvaluationAgent(BaseAgent):
    """
    EvaluationAgent class to assess and compare model-generated responses.

    This agent uses a DeBERTa-based model to evaluate the similarity between
    two text outputs (e.g., from different models) based on Precision, Recall, and F1 Score.

    Attributes:
    -----------
    model_name : str
        Path to the DeBERTa model used for evaluation. The model will be downloaded and saved
        locally if it doesn't already exist in the specified path.

    Methods:
    --------
    evaluate(allam_output: str, gpt_output: str) -> tuple:
        Compares two text outputs and returns the mean Precision, Recall, and F1 Score.
    """

    def __init__(self):
        """
        Initializes the EvaluationAgent.

        Checks if the specified DeBERTa model exists locally. If not, downloads the model and
        tokenizer, and saves them to the configured path.
        """
        # Check if the model exists locally
        if Config.DEBERTA_LARGE_MODEL_PATH.exists():
            print(f"Loading model from local path: {Config.DEBERTA_LARGE_MODEL_PATH}", flush=True)
        else:
            print(f"Local path not found. Downloading model: {Config.DEBERTA_MODEL_NAME}", flush=True)
            
            # Create the directory if it doesn't exist
            os.makedirs(str(Config.DEBERTA_LARGE_MODEL_PATH), exist_ok=True)

            # Download and save model and tokenizer
            tokenizer = AutoTokenizer.from_pretrained(Config.DEBERTA_MODEL_NAME)
            model = AutoModel.from_pretrained(Config.DEBERTA_MODEL_NAME)
            
            model.save_pretrained(str(Config.DEBERTA_LARGE_MODEL_PATH))
            tokenizer.save_pretrained(str(Config.DEBERTA_LARGE_MODEL_PATH))

        self.model_name = Config.DEBERTA_LARGE_MODEL_PATH

    def evaluate(self, allam_output: str, gpt_output: str) -> tuple:
        """
        Evaluates the similarity between the Allam model output and the GPT output.

        Uses BERTScore to calculate Precision, Recall, and F1 Score between the candidate 
        output (Allam) and the reference output (GPT).

        :param allam_output: The generated text output from the Allam model.
        :param gpt_output: The reference text output from the GPT model.
        :return: A tuple containing the mean Precision, Recall, and F1 Score.
        """
        reference = [gpt_output]
        candidate = [allam_output]

        # Calculate BERTScore using the specified model
        (P, R, F), hashname = score(candidate, reference, model_type=self.model_name, return_hash=True)

        # Return mean Precision, Recall, and F1 Score
        return P.mean().item(), R.mean().item(), F.mean().item()
