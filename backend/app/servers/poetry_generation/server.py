# Import necessary modules
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware

from ibm_watsonx_ai.metanames import GenTextParamsMetaNames  # Parameters for text generation

# Import custom modules for the application
from backend.app.agents.poetry_generation_agent import PoetryGenerationAgent  # Agent for handling poetry generation
from backend.app.servers.poetry_generation.generation import generate  # Function to generate poetry based on input
from backend.app.models import LLMModel  # Language model class for text generation
from backend.app.utils.debate import *  # Utilities for debate (may include helper functions or constants)
from backend.app.config.config import Config  # Configuration settings

# Initialize FastAPI application
app = FastAPI()

# Enable CORS (Cross-Origin Resource Sharing) to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin
    allow_credentials=True,  # Allow credentials to be sent with requests
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers in requests
)

# Load embeddings for thematic and poet data to facilitate similarity search in text generation
index_theme = load_embeddings(path=Config.THEME_EMBEDDINGS_PATH)  # Load theme embeddings
index_poet = load_embeddings(path=Config.POET_EMBEDDINGS_PATH)  # Load poet embeddings

# Define parameters for different Large Language Models (LLMs)

# Parameters for the retriever LLM used to retrieve relevant text or poetry
retriever_parameters = {
    GenTextParamsMetaNames.MAX_NEW_TOKENS: 1500,  # Maximum number of tokens to generate
    GenTextParamsMetaNames.DECODING_METHOD: "greedy",  # Decoding strategy for deterministic output
    GenTextParamsMetaNames.REPETITION_PENALTY: 1,  # Penalty for repeated tokens
    GenTextParamsMetaNames.TEMPERATURE: 0.3,  # Controls randomness in generation (lower is more deterministic)
}

# Parameters for the generator LLM used to generate new poetic text
generator_parameters = {
    GenTextParamsMetaNames.MAX_NEW_TOKENS: 120,  # Maximum tokens for the generator model
    GenTextParamsMetaNames.REPETITION_PENALTY: 1.1,  # Slight penalty for repetition
    GenTextParamsMetaNames.TEMPERATURE: 0.4,  # Moderate randomness for creative output
}

# Initialize retriever and generator LLM models
retriever_llm = LLMModel(retriever_parameters)
generator_llm = LLMModel(generator_parameters)

# Define the Poetry Generation Agent, responsible for managing the LLMs, embeddings, and data
generator_agent = PoetryGenerationAgent(
    generator_llm_model=generator_llm,  # Generator LLM model instance
    retriever_llm_model=retriever_llm,  # Retriever LLM model instance
    index_poet=index_poet,  # Poet embeddings
    index_theme=index_theme,  # Theme embeddings
    poets_list=POETS,  # List of poets (may come from a predefined list)
    themes_list=THEMES,  # List of themes
    poetry_database_path=Config.ASHAAR_DATA_PATH  # Path to the poetry database
)

# Define WebSocket endpoint for real-time text generation
@app.websocket("/wss/generate")
async def websocket_endpoint(websocket: WebSocket, prompt: str = Query(...)):
    """
    WebSocket endpoint to generate poetry based on a user-provided prompt.
    - Accepts a 'prompt' query parameter from the client.
    - Uses the PoetryGenerationAgent to generate text in response to the prompt.
    """
    await websocket.accept()  # Accept WebSocket connection
    try:
        await generate(
            websocket,  # WebSocket connection to communicate with the client
            prompt,  # Prompt provided by the client for poetry generation
            generator_agent=generator_agent  # Poetry generation agent instance
        )
    except WebSocketDisconnect:
        print("WebSocket disconnected")  # Handle client disconnection
    except Exception as e:
        print(f"Error: {e}")  # Log any other errors

# Main entry point to run the FastAPI app with Uvicorn (ASGI server)
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Run server on all available IPs at port 8000
