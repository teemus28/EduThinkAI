import os
import faiss
import numpy as np
import pickle
from typing import List, Any
from huggingface_hub import InferenceClient
from EduThinkAI.embedding import EmbeddingPipeline
from dotenv import load_dotenv

load_dotenv()

class FaissVectorStore:
    def __init__(self, persist_dir: str = "faiss_store", embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2", chunk_size: int = 1000, chunk_overlap: int = 200):
        self.persist_dir = persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)
        self.index = None
        self.metadata = []
        self.embedding_model = embedding_model
        self.client = InferenceClient(token=os.getenv("HF_TOKEN"))
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        print(f"[INFO] Using HF Inference API for embeddings: {embedding_model}")

    def _embed(self, texts: List[str]) -> np.ndarray:
        result = self.client.feature_extraction(texts, model=self.embedding_model)
        return np.array(result).astype('float32')

    def query(self, query_text: str, top_k: int = 5):
        query_emb = self._embed([query_text])
        return self.search(query_emb, top_k=top_k)
    
    def add_embeddings(self, embeddings: np.ndarray, metadatas: List[Any] = None):
        dim = embeddings.shape[1]
        if self.index is None:
            self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        if metadatas:
            self.metadata.extend(metadatas)
        print(f"[INFO] Added {embeddings.shape[0]} vectors to Faiss index.")

    def save(self):
        faiss_path = os.path.join(self.persist_dir, "faiss.index")
        meta_path = os.path.join(self.persist_dir, "metadata.pkl")
        faiss.write_index(self.index, faiss_path)
        with open(meta_path, "wb") as f:
            pickle.dump(self.metadata, f)
        print(f"[INFO] Saved Faiss index and metadata to {self.persist_dir}")

    def load(self):
        faiss_path = os.path.join(self.persist_dir, "faiss.index")
        meta_path = os.path.join(self.persist_dir, "metadata.pkl")
        self.index = faiss.read_index(faiss_path)
        with open(meta_path, "rb") as f:
            self.metadata = pickle.load(f)
        print(f"[INFO] Loaded Faiss index and metadata from {self.persist_dir}")

    def search(self, query_embedding: np.ndarray, top_k: int = 5):
        D, I = self.index.search(query_embedding, top_k)
        results = []
        for idx, dist in zip(I[0], D[0]):
            meta = self.metadata[idx] if idx < len(self.metadata) else None
            results.append({"index": idx, "distance": dist, "metadata": meta})
        return results


if __name__ == "__main__":
    from EduThinkAI.data_loader import load_all_documents
    docs = load_all_documents("data")
    store = FaissVectorStore("faiss_store")
    store.build_from_documents(docs)
    store.load()
    print(store.query("What is attention mechanism?", top_k=3))
