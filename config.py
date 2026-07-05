from dotenv import load_dotenv
import os

load_dotenv()  # reads .env file into environment variables

HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError(
        "HF_TOKEN not found. Add it to your .env file as HF_TOKEN=your_token_here"
    )

MODEL_ID = "google/gemma-3-4b-it"
UPLOAD_DIR = "uploads"
MINDMAP_OUTPUT_DIR = "static/mindmaps"
MAX_CHUNKS = 15
CHUNK_SIZE = 4000
CHUNK_OVERLAP = 200