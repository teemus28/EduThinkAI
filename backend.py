from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import shutil, os, uuid
from contextlib import asynccontextmanager

from models.gemma_model import load_model
from extractor.load_files import extract_text
from tree_generator import generate_mindmap_structure
from graph_builder import build_mindmap_graph
from graph_builder import display_mindmap

from config import UPLOAD_DIR, MINDMAP_OUTPUT_DIR


# 1. Create directories immediately during script loading
os.makedirs("static", exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Keep your other startup logic here
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(MINDMAP_OUTPUT_DIR, exist_ok=True)
    load_model()
    yield

# 2. Initialize FastAPI
app = FastAPI(lifespan=lifespan)

# 3. Mount now works because the folder exists
app.mount("/static", StaticFiles(directory="static"), name="static")





@app.post("/generate")
async def generate(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    text = extract_text(file_path)
    tree = generate_mindmap_structure(text)
    html_path = build_mindmap_graph(tree)

    return {"tree": tree, "mindmap_url": f"/{html_path}"}