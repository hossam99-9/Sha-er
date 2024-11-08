# Import necessary modules
from pydantic import BaseModel  # For data validation and serialization
import uvicorn

from fastapi import FastAPI, HTTPException  # FastAPI for creating APIs, HTTPException for error handling
from fastapi.middleware.cors import CORSMiddleware  # CORS middleware for cross-origin requests

# Import custom functions for poetry analysis
from backend.app.servers.poetry_analysis.criticism.critic import critic_bait  # For analyzing poetry criticism
from backend.app.servers.poetry_analysis.meters.model import predict_meter  # For predicting the meter of the poem
from backend.app.servers.poetry_analysis.qafya.rhyme import predict_qafya  # For predicting rhyme scheme
from backend.app.servers.poetry_analysis.rhetorical.chain import get_rhetorical_analysis  # For rhetorical analysis
from backend.app.utils.debate import *  # Importing utilities for logging, etc.

# Initialize FastAPI application
app = FastAPI()

# Enable CORS to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins to make requests
    allow_credentials=True,  # Allows credentials to be included in requests
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Function to check if the input text contains only Arabic characters and spaces
def is_arabic_only(text):
    # Define Unicode ranges for Arabic characters
    arabic_ranges = (
        ('\u0621', '\u063A'),  # Arabic letters in Unicode
        ('\u0641', '\u0655')   # Additional Arabic letters and diacritics
    )

    # Check if each character is an Arabic character or whitespace
    def is_arabic_char(char):
        return char.isspace() or any(ord(start) <= ord(char) <= ord(end) for start, end in arabic_ranges)
    
    # Return True if all characters in the text are Arabic or whitespace
    return all(is_arabic_char(char) for char in text)

# Define a data model for the input text
class TextInput(BaseModel):
    bait: str  # A single line of poetry in Arabic

# Define a data model for the prediction output
class PredictionOutput(BaseModel):
    qafya: str  # Predicted rhyme scheme
    meter: str  # Predicted meter
    critic: str  # Critique of the poetry
    rhetorical: str  # Rhetorical analysis result

# API endpoint to analyze poetry
@app.post("/analysis", response_model=PredictionOutput)
async def predict(data: TextInput):
    """
    Endpoint to analyze a line of Arabic poetry.
    - Validates that the input contains only Arabic characters.
    - Returns predictions for rhyme (qafya), meter, critique, and rhetorical analysis.
    """
    # Check if the input text contains only Arabic characters
    if not is_arabic_only(data.bait):
        log_message(msg="Please try another bait", level=2)  # Log a message if validation fails
        # Return empty results with a message to enter valid text in Arabic
        return PredictionOutput(
            qafya="",
            meter="",
            critic="",
            rhetorical="يرجي إدخال بيت صحيح"
        )
    try:
        # Perform poetry analysis functions
        critic_result = critic_bait(data.bait)  # Get critique
        meter = predict_meter(data.bait)  # Predict meter
        qafya = predict_qafya(data.bait)  # Predict rhyme scheme
        rhetorical = get_rhetorical_analysis(data.bait)  # Get rhetorical analysis

        # Return the analysis results as a response
        return PredictionOutput(
            qafya=qafya,
            meter=meter,
            critic=critic_result,
            rhetorical=rhetorical
        )
    except Exception as e:
        # Handle and raise exceptions with a 400 status code if any issue occurs during processing
        raise HTTPException(status_code=400, detail=str(e))

# Main entry point to run the FastAPI app with Uvicorn
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Run server on all available IPs at port 8000
