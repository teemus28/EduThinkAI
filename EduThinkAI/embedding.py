
from EduThinkAI.data_loader import load_all_documents

import os
import numpy as np
from typing import List, Any
from huggingface_hub import InferenceClient
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

class EmbeddingPipeline:
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        hf_token: str = None,
        batch_size: int = 32,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.model_name = model_name
        self.batch_size = batch_size
        self.client = InferenceClient(token=hf_token or os.getenv("HF_TOKEN"))
        print(f"[INFO] Using HF Inference API for embeddings: {model_name}")

    def chunk_documents(self, documents: List[Any]) -> List[Any]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_documents(documents)
        print(f"[INFO] Split {len(documents)} documents into {len(chunks)} chunks.")
        return chunks

    def embed_chunks(self, chunks: List[Any]) -> np.ndarray:
        texts = [chunk.page_content for chunk in chunks]
        print(f"[INFO] Generating embeddings for {len(texts)} chunks via HF API...")

        all_embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            result = self.client.feature_extraction(batch, model=self.model_name)
            all_embeddings.extend(np.array(result))
            print(f"[INFO] Embedded {min(i + self.batch_size, len(texts))}/{len(texts)}")

        embeddings = np.array(all_embeddings).astype('float32')
        print(f"[INFO] Embeddings shape: {embeddings.shape}")
        return embeddings

    def embed_query(self, text: str) -> np.ndarray:
        """Single-text embedding for query time (used by vector_store.query)."""
        result = self.client.feature_extraction([text], model=self.model_name)
        return np.array(result).astype('float32')
    
    

# Example usage
if __name__ == "__main__":
    
    docs = load_all_documents("data")
    emb_pipe = EmbeddingPipeline()
    chunks = emb_pipe.chunk_documents(docs)
    embeddings = emb_pipe.embed_chunks(chunks)
    print("[INFO] Example embedding:", embeddings[0] if len(embeddings) > 0 else None)
