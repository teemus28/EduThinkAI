from models.gemma_model import ask_gemma_visual
import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from PIL import Image


def extract_text(file_path):
    """Extract text from pdf, txt, or image files."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        return "\n".join([p.page_content for p in pages])

    elif ext == ".txt":
        loader = TextLoader(file_path)
        docs = loader.load()
        return "\n".join([d.page_content for d in docs])

    elif ext in [".jpg", ".jpeg", ".png", ".webp"]:
        extracted = ask_gemma_visual(
            image=file_path, # Pass the image path directly
            prompt="Extract and transcribe all readable text and key visual concepts "
                   "from this image. If it's a diagram, describe its structure. "
                   "Return only the content, no commentary."
        )
        return extracted

    else:
        raise ValueError(f"Unsupported file type: {ext}")