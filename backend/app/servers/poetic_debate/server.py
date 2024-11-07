import os
import csv

import uvicorn

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware

from ibm_watsonx_ai.metanames import GenTextParamsMetaNames

from backend.app.agents.poetry_generation_agent import PoetryGenerationAgent
from backend.app.agents.poetry_judge_agent import PoetryJudgeAgent
from backend.app.models import LLMModel
from backend.app.servers.poetic_debate.simulation import run_simulation
from backend.app.utils.debate import *
from backend.app.config.config import Config

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load embeddings for themes and poets lists
index_theme = load_embeddings(path=Config.THEME_EMBEDDINGS_PATH)
index_poet = load_embeddings(path=Config.POET_EMBEDDINGS_PATH)

filename = str(Config.EVALUATION_RESULTS_GPT_LIKE_PATH) + "/data.csv"
os.makedirs(str(Config.EVALUATION_RESULTS_GPT_LIKE_PATH), exist_ok=True)
headers = ["Round", "GPT-comment1", "GPT-comment2", "Allam-comment1", "Allam-comment2", "GPT-summary", "Allam-summary", "comment1-scores", "comment2-scores", "summary-scores"]

with open(filename, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(headers)  # Write the header row

# Define LLMs
# TODO: Tune temperatures
commentator_parameters = {
    GenTextParamsMetaNames.MAX_NEW_TOKENS: 1500,
    GenTextParamsMetaNames.REPETITION_PENALTY: 1,
    GenTextParamsMetaNames.TEMPERATURE: 0.3,
}

summarizer_parameters = {
    GenTextParamsMetaNames.MAX_NEW_TOKENS: 1500,
    GenTextParamsMetaNames.REPETITION_PENALTY: 1,
    GenTextParamsMetaNames.TEMPERATURE: 0.3,
}

commentator_llm = LLMModel(commentator_parameters)

summarizer_llm = LLMModel(summarizer_parameters)

# Define agent
judge_agent = PoetryJudgeAgent(commentator_llm_model=commentator_llm,
                               summarizer_llm_model=summarizer_llm,)
                               
# Define LLMs
retriever_parameters = {
    GenTextParamsMetaNames.MAX_NEW_TOKENS: 1500,
    GenTextParamsMetaNames.DECODING_METHOD: "greedy",
	GenTextParamsMetaNames.REPETITION_PENALTY: 1,
    GenTextParamsMetaNames.TEMPERATURE: 0.3,
}

generator_parameters = {
    GenTextParamsMetaNames.MAX_NEW_TOKENS: 120,
    GenTextParamsMetaNames.REPETITION_PENALTY: 1.1,
    GenTextParamsMetaNames.TEMPERATURE: 0.4,
}

retriever_llm = LLMModel(retriever_parameters)
generator_llm = LLMModel(generator_parameters)

# Define agent
generator_agent = PoetryGenerationAgent(generator_llm_model=generator_llm,
                                        retriever_llm_model=retriever_llm,
                                        index_poet=index_poet,
                                        index_theme=index_theme,
                                        poets_list=POETS,
                                        themes_list=THEMES,
                                        poetry_database_path = Config.ASHAAR_DATA_PATH)
# WebSocket endpoint
@app.websocket("/wss/battle")
async def websocket_endpoint(
    websocket: WebSocket,
    poet1: str = Query(...),
    poet2: str = Query(...),
    topics: str = Query(...)
):
    await websocket.accept()
    
    ROUND_THEMES = topics.split(',')

    try:
        await run_simulation(websocket,
                            round_themes=ROUND_THEMES,
                            poet1=poet1,
                            poet2=poet2,
                            generator_agent=generator_agent,
                            judge_agent=judge_agent,
                            log_file= filename)
    except WebSocketDisconnect:
        print("WebSocket disconnected")

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
