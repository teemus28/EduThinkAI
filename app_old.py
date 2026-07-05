import os
import shutil
import uuid

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from extractor.load_files import extract_text
from tree_generator import generate_mindmap_structure
from graph_builder import build_mindmap_graph

app = FastAPI(
    title="Mind Map Generator API",
    description="Generate interactive HTML mind maps from PDFs, images and documents.",
    version="1.0"
)

# ----------------------------------------
# CORS
# ----------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ----------------------------------------
# Home
# ----------------------------------------

@app.get("/")
def home():
    return {
        "message": "Mind Map Generator API is running."
    }



@app.get("/mindmap/{filename}")
async def get_mindmap(filename: str):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(file_path):
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(file_path, media_type="text/html")
# ----------------------------------------
# Generate Mind Map
# ----------------------------------------

@app.post("/generate")
async def generate_mindmap(file: UploadFile = File(...)):

    try:

        extension = file.filename.split(".")[-1]

        filename = f"{uuid.uuid4()}.{extension}"

        upload_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # -----------------------------
        # Extract Text
        # -----------------------------

        text = extract_text(upload_path)

        # -----------------------------
        # Generate Tree
        # -----------------------------

        tree = generate_mindmap_structure(text)

        # -----------------------------
        # Build Graph
        # -----------------------------


        html_name = f"{uuid.uuid4()}.html"
        html_path = os.path.join(OUTPUT_FOLDER, html_name)

        build_mindmap_graph(
            tree,
            output_file=html_path
        )
        return JSONResponse(
    {
        "success": True,
        "tree": tree,
        "html_file": html_name,
        "download_url": f"/mindmap/{html_name}"
    }
)

        # html_path = build_mindmap_graph(
        #     tree,
        #     output_dir=OUTPUT_FOLDER
        # )

        # html_name = os.path.basename(html_path)

        # return JSONResponse(
        #     {
        #         "success": True,
        #         "tree": tree,
        #         "html_file": html_name,
        #         "download_url": f"/mindmap/{html_name}"
        #     }
        # )


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))