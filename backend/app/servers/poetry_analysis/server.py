from pydantic import BaseModel

import uvicorn

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException

from backend.app.servers.poetry_analysis.criticism.critic import critic_bait
from backend.app.servers.poetry_analysis.meters.model import predict_meter
from backend.app.servers.poetry_analysis.qafya.rhyme import predict_qafya
from backend.app.servers.poetry_analysis.rhetorical.chain import get_rhetorical_analysis
from backend.app.utils.debate import *

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def is_arabic_only(text):
    arabic_ranges = (
        ('\u0621', '\u063A'),
        ('\u0641', '\u0655')
    )

    def is_arabic_char(char):
        return char.isspace() or any(ord(start) <= ord(char) <= ord(end) for start, end in arabic_ranges)
    
    return all(is_arabic_char(char) for char in text)

class TextInput(BaseModel):
    bait: str

class PredictionOutput(BaseModel):
    qafya: str
    meter: str
    critic: str
    rhetorical: str

@app.post("/analysis", response_model=PredictionOutput)
async def predict(data: TextInput):

  if is_arabic_only(data.bait) == False:
    log_message(msg=f"Please try another bait",level=2)
    return PredictionOutput(qafya="",
                          meter="",
                          critic="",
                          rhetorical="يرجي إدخال بيت صحيح")
  try:
    critic_result = critic_bait(data.bait)
    meter = predict_meter(data.bait)
    qafya = predict_qafya(data.bait)
    rhetorical = get_rhetorical_analysis(data.bait)

    return PredictionOutput(qafya=qafya,
                            meter=meter,
                            critic=critic_result,
                            rhetorical=rhetorical)
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))

if __name__ == '__main__':
  uvicorn.run(app, host="0.0.0.0", port=8000)