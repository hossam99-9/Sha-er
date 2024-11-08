# Standard library imports
import os  # For file system operations
import csv  # For working with CSV files

# FastAPI-related imports
import uvicorn  # ASGI server for FastAPI
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query  # FastAPI components
from fastapi.middleware.cors import CORSMiddleware  # Middleware for handling CORS

# IBM Watsonx imports
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames  # Parameters for IBM Watsonx text generation

# Import custom modules for agents, models, and utilities
from backend.app.agents.poetry_generation_agent import PoetryGenerationAgent  # Agent for generating poetry
from backend.app.agents.poetry_judge_agent import PoetryJudgeAgent  # Agent for judging poetry
from backend.app.models import LLMModel  # Language model handler for generation and judging
from backend.app.servers.poetic_debate.simulation import run_simulation  # Function to simulate a poetic debate
from backend.app.utils.debate import *  # Utility functions for the debate module
from backend.app.config.config import Config  # Configuration settings

# Initialize the FastAPI application
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from all origins
    allow_credentials=True,  # Allow cookies and other credentials to be sent with requests
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers in requests
)

# Load embeddings for themes and poets used in text generation
index_theme = load_embeddings(path=Config.THEME_EMBEDDINGS_PATH)
index_poet = load_embeddings(path=Config.POET_EMBEDDINGS_PATH)

# Setup for storing evaluation results in a CSV file
filename = str(Config.EVALUATION_RESULTS_GPT_LIKE_PATH) + "/data.csv"
os.makedirs(str(Config.EVALUATION_RESULTS_GPT_LIKE_PATH), exist_ok=True)  # Ensure the directory exists
headers = ["Round", "GPT-comment1", "GPT-comment2", "Allam-comment1", "Allam-comment2", 
           "GPT-summary", "Allam-summary", "comment1-scores", "comment2-scores", "summary-scores"]

# Create the CSV file and write the header row
with open(filename, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(headers)

# Define parameters for the commentator and summarizer models used in judging poetry
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

# Initialize LLM models for commentary and summarization
commentator_llm = LLMModel(commentator_parameters)
summarizer_llm = LLMModel(summarizer_parameters)

# Instantiate a PoetryJudgeAgent using the commentator and summarizer models
judge_agent = PoetryJudgeAgent(
    commentator_llm_model=commentator_llm,
    summarizer_llm_model=summarizer_llm,
)

# Define parameters for the retriever and generator LLMs used in generating poetry
retriever_parameters = {
    GenTextParamsMetaNames.MAX_NEW_TOKENS: 1500,
    GenTextParamsMetaNames.DECODING_METHOD: "greedy",  # Greedy decoding for deterministic output
    GenTextParamsMetaNames.REPETITION_PENALTY: 1,
    GenTextParamsMetaNames.TEMPERATURE: 0.3,
}

generator_parameters = {
    GenTextParamsMetaNames.MAX_NEW_TOKENS: 120,
    GenTextParamsMetaNames.REPETITION_PENALTY: 1.1,
    GenTextParamsMetaNames.TEMPERATURE: 0.4,
}

# Initialize the retriever and generator models
retriever_llm = LLMModel(retriever_parameters)
generator_llm = LLMModel(generator_parameters)

# Instantiate a PoetryGenerationAgent using the generator and retriever models
generator_agent = PoetryGenerationAgent(
    generator_llm_model=generator_llm,
    retriever_llm_model=retriever_llm,
    index_poet=index_poet,  # Embeddings for poets
    index_theme=index_theme,  # Embeddings for themes
    poets_list=POETS,  # List of poets
    themes_list=THEMES,  # List of themes
    poetry_database_path=Config.ASHAAR_DATA_PATH,  # Path to poetry database
)

# WebSocket endpoint for conducting a "poetry battle" simulation
@app.websocket("/wss/battle")
async def websocket_endpoint(
    websocket: WebSocket,
    poet1: str = Query(...),  # First poet's name
    poet2: str = Query(...),  # Second poet's name
    topics: str = Query(...)  # Themes for the debate, separated by commas
):
    await websocket.accept()  # Accept the WebSocket connection
    
    ROUND_THEMES = topics.split(',')  # Split the topics into a list of themes

    try:
        # Run the poetry battle simulation with the provided agents and topics
        await run_simulation(
            websocket=websocket,
            round_themes=ROUND_THEMES,
            poet1=poet1,
            poet2=poet2,
            generator_agent=generator_agent,
            judge_agent=judge_agent,
            log_file=filename,  # Log results to the CSV file
        )
    except WebSocketDisconnect:
        print("WebSocket disconnected")  # Handle WebSocket disconnection

# Entry point to run the FastAPI application with Uvicorn
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
