import uvicorn

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware

from ibm_watsonx_ai.metanames import GenTextParamsMetaNames

from backend.app.agents.poetry_generation_agent import PoetryGenerationAgent
from backend.app.servers.poetry_generation.generation import generate
from backend.app.models import LLMModel
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

# Define LLMS
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

# Define Agent
generator_agent = PoetryGenerationAgent(generator_llm_model=generator_llm,
                                        retriever_llm_model=retriever_llm,
                                        index_poet=index_poet,
                                        index_theme=index_theme,
                                        poets_list=POETS,
                                        themes_list=THEMES,
                                        poetry_database_path = Config.ASHAAR_DATA_PATH)
# WebSocket endpoint
@app.websocket("/ws/generate")
async def websocket_endpoint(websocket: WebSocket,
                             prompt: str = Query(...)):

    await websocket.accept()
    try:
        await generate(websocket,
                       prompt,
                       generator_agent=generator_agent)

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
