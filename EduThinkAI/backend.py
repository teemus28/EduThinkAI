import os
import shutil
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from dotenv import load_dotenv

from EduThinkAI.search import Gemma3RAGChatbot

load_dotenv()

# -----------------------------
# Global Chatbot
# -----------------------------
chatbot = None

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -----------------------------
# Lifespan
# -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    global chatbot

    print("=" * 60)
    print("Loading RAG Chatbot...")
    print("=" * 60)

    chatbot = Gemma3RAGChatbot()

    print("Chatbot Loaded Successfully!")
    print("=" * 60)

    yield

    print("Shutting down...")


# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(
    title="Gemma-3 RAG Chatbot API",
    version="1.0",
    description="RAG Chatbot using FAISS + Gemma 3",
    lifespan=lifespan,
)


# -----------------------------
# Routes
# -----------------------------
@app.get("/")
def root():
    return {
        "message": "Gemma-3 RAG Chatbot API is Running!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "chatbot_loaded": chatbot is not None
    }


@app.post("/chat")
async def chat(
    query: str = Form(...),
    image: Optional[UploadFile] = File(None)
):
    global chatbot

    if chatbot is None:
        raise HTTPException(
            status_code=500,
            detail="Chatbot not initialized."
        )

    image_path = None

    try:
        # Save uploaded image if present
        if image is not None:
            image_path = os.path.join(UPLOAD_FOLDER, image.filename)

            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

        answer = chatbot.generate_response(
            query=query,
            image=image_path
        )

        return {
            "success": True,
            "query": query,
            "answer": answer
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)