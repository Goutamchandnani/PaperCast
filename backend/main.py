from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from routes import podcast

app = FastAPI(title="PaperCast API")

# Configure CORS for React frontend (Vite default port is 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(podcast.router, prefix="/api/podcast", tags=["podcast"])

@app.get("/")
def health_check():
    return {"status": "ok", "message": "PaperCast API is running"}
