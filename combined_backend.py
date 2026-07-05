import os
import shutil
import uuid
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

# -------------------------------
# Chatbot Imports
# -------------------------------

from EduThinkAI.search import Gemma3RAGChatbot

# -------------------------------
# Mind Map Imports
# -------------------------------

from extractor.load_files import extract_text
from tree_generator import generate_mindmap_structure
from graph_builder import build_mindmap_graph

load_dotenv()

# =====================================================
# Global Objects
# =====================================================

chatbot = None

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# =====================================================
# Lifespan
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    global chatbot

    print("=" * 60)
    print("Loading Gemma RAG Chatbot...")
    print("=" * 60)

    chatbot = Gemma3RAGChatbot()

    print("Chatbot Loaded Successfully!")

    yield

    print("Server Shutdown")


# =====================================================
# FastAPI
# =====================================================

app = FastAPI(
    title="EduThink AI",
    version="1.0",
    description="AI Toolkit (Mind Map + RAG Chatbot)",
    lifespan=lifespan,
)

# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# Root
# =====================================================

@app.get("/")
def home():
    return {
        "message": "EduThink AI API Running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "chatbot_loaded": chatbot is not None
    }


# =====================================================
# CHATBOT APIs
# =====================================================

@app.post("/chatbot/chat")
async def chat(
    query: str = Form(...),
    image: Optional[UploadFile] = File(None)
):

    global chatbot

    if chatbot is None:
        raise HTTPException(
            status_code=500,
            detail="Chatbot not initialized"
        )

    image_path = None

    try:

        if image:

            image_path = os.path.join(
                UPLOAD_FOLDER,
                image.filename
            )

            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(
                    image.file,
                    buffer
                )

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


@app.get("/chatbot/health")
def chatbot_health():
    return {
        "status": "healthy"
    }


# =====================================================
# MIND MAP APIs
# =====================================================

@app.post("/mindmap/generate")
async def generate_mindmap(
    file: UploadFile = File(...)
):

    try:

        extension = file.filename.split(".")[-1]

        filename = f"{uuid.uuid4()}.{extension}"

        upload_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        text = extract_text(upload_path)

        tree = generate_mindmap_structure(text)

        html_name = f"{uuid.uuid4()}.html"

        html_path = os.path.join(
            OUTPUT_FOLDER,
            html_name
        )

        build_mindmap_graph(
            tree,
            output_file=html_path
        )

        return {
            "success": True,
            "tree": tree,
            "html_file": html_name,
            "download_url": f"/mindmap/{html_name}"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/mindmap/{filename}")
async def get_mindmap(filename: str):

    file_path = os.path.join(
        OUTPUT_FOLDER,
        filename
    )

    if not os.path.exists(file_path):

        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    return FileResponse(
        file_path,
        media_type="text/html"
    )