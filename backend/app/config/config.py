# config.py

from pathlib import Path

class Config:

    # Allam Model Configs
    IBM_CLOUD_URL = "https://eu-de.ml.cloud.ibm.com"
    LLM_MODEL_NAME = "sdaia/allam-1-13b-instruct"
    IBM_API_KEY = "a2F0DVBnfePotsn-P7K5iIAoHOTUC3-SyS4G2YW5CUFK"
    PROJECT_ID = "85b95f9c-2602-4bbe-85cf-abae5a6bb091"

    # Other configuration settings
    LOGGER_LEVEL = 2
    # Use this to generate metrics for evaluating Allam model itself against gpt-4
    EVALUATION_MODE = False

    OPENAI_API_KEY = "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"
    LANGCHAIN_API_KEY = ""

    # Data
    current_dir = Path(__file__).parent
    project_root = current_dir.parent

    ASHAAR_DATA_PATH = project_root / 'data_folder' / 'ashaar.csv'
    POET_EMBEDDINGS_PATH = project_root / 'data_folder' / 'poet_embeddings.pkl'
    THEME_EMBEDDINGS_PATH = project_root / 'data_folder' / 'theme_embeddings.pkl'
    METERS_MODEL_WEIGHTS = project_root / 'data_folder' / 'meters.weights.h5'
    BALAGA_KNOWLEDGE_BASE_PATH = project_root / 'data_folder' / 'balaga.txt'
    EVALUATION_RESULTS_GPT_LIKE_PATH = project_root / 'data_folder' / 'evaluation' / 'gpt-4-like'

    # Embedding models
    LABSE_MODEL_PATH = project_root / 'data_folder' / 'models' / 'LaBSE'
    PARAPHRASE_MODEL_PATH = project_root / 'data_folder' / 'models' / 'paraphrase-multilingual-mpnet-base-v2'
    DEBERTA_LARGE_MODEL_PATH = project_root / 'data_folder' / 'models' / 'microsoft' / 'deberta-large-mnli'
