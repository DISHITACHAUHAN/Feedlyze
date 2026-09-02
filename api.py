from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types
import os

load_dotenv(Path(__file__).parent / ".env")
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY is not loaded. Check your .env file.")

client = genai.Client(api_key=api_key)

app = FastAPI()

#what the caller must send us
class Review(BaseModel):
    text: str
# what gemmi gives back, and what we send to caller
# we keep it on purpose --> fewer token used.
class Analysis(BaseModel):
    label: str 
    score: int
    theme: str 

@app.post("/analyzer")
def analyze(review: Review):
    response = client.models.generate_content(
         model = "gemini-3.5-flash-lite",
         contents=(
             "Analyze this customer review.\n"
             "label must be 'positive', 'negative', or 'neutral'.\n"
             "score must be a number from 1 (very bad) to 5 (very good). \n"
             "theme must be one lowercase word for main topic "
             "(for example: delivery, taste, price, service, quality).\n"
             f"Review: {review.text}"
         ),
         config = types.GenerateContentConfig(
             response_mime_type="application/json",
             response_schema=Analysis,
         ),
    )
    return response.parsed