import os
import base64
import mimetypes
from pathlib import Path
from typing import Optional, Union, List, Dict, Any

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from EduThinkAI.vector_store import FaissVectorStore

load_dotenv()


class Gemma3RAGChatbot:
    """
    RAG chatbot powered by Gemma 3 (via HF InferenceClient), backed by a
    FAISS vector store, with:
      1. Auto-load existing FAISS index, or build one from PDFs if missing
      2. Context-aware answering with automatic fallback to the model's
         own knowledge if no relevant context is retrieved
      3. Image input support (Gemma 3 is multimodal)
    """

    def __init__(
        self,
        persist_dir: str = "faiss_store",
        embedding_model: str = "all-MiniLM-L6-v2",
        llm_model: str = "google/gemma-3-4b-it",
        pdf_dir: str = "pdf_files",
        temperature: float = 0.1,
        max_tokens: int = 512,
        top_k: int = 5,
        score_threshold: Optional[float] = None,
        hf_token: Optional[str] = None,
    ):
        """
        Args:
            persist_dir: Directory containing faiss.index + metadata.pkl
            embedding_model: SentenceTransformer model name for embeddings
            llm_model: Gemma 3 model id (must support vision, e.g. -it models)
            pdf_dir: Folder of PDFs used to build the index if none exists
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            top_k: Default number of chunks to retrieve
            score_threshold: If your vectorstore results carry a 'score' or
                              'distance' key in metadata, results below this
                              similarity are dropped. Leave None to disable
                              (matches original RAGSearch behavior — any
                              non-empty retrieved text counts as "found").
            hf_token: HF API token. Falls back to HF_TOKEN env var if not passed.
        """
        # -------------------------
        # Load / build FAISS Vector Store
        # -------------------------
        self.vectorstore = FaissVectorStore(persist_dir, embedding_model)

        faiss_path = os.path.join(persist_dir, "faiss.index")
        meta_path = os.path.join(persist_dir, "metadata.pkl")

        if not (os.path.exists(faiss_path) and os.path.exists(meta_path)):
            print(f"[INFO] No existing FAISS index found at '{persist_dir}'. Building new index...")
            from EduThinkAI.data_loader import load_all_documents

            docs = load_all_documents(pdf_dir)
            self.vectorstore.build_from_documents(docs)
            print("[INFO] FAISS index built and persisted.")
        else:
            self.vectorstore.load()
            print(f"[INFO] Loaded existing FAISS index from '{persist_dir}'.")

        # -------------------------
        # Initialize HuggingFace LLM (Gemma 3)
        # -------------------------
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            raise ValueError("Hugging Face API token is required (pass hf_token or set HF_TOKEN env var).")

        self.model_name = llm_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_k = top_k
        self.score_threshold = score_threshold

        self.client = InferenceClient(
            model=self.model_name,
            token=hf_token,
        )

        print(f"[INFO] HuggingFace LLM initialized: {llm_model}")

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------
    def _retrieve_context(self, query: str, top_k: Optional[int] = None) -> str:
        """
        Fetch relevant chunks from FAISS via vectorstore.query(). Returns
        an empty string if nothing relevant is found, which triggers
        model-only fallback in generate_response().
        """
        top_k = top_k or self.top_k

        try:
            results: List[Dict[str, Any]] = self.vectorstore.query(query, top_k=top_k)
        except Exception as e:
            print(f"[WARN] Retrieval failed, falling back to model-only response: {e}")
            return ""

        if not results:
            return ""

        chunks = []
        for r in results:
            metadata = r.get("metadata")
            if not metadata:
                continue

            text = metadata.get("text", "").strip()
            if not text:
                continue

            # Optional score filtering, only applied if both a threshold
            # and a score/distance field are actually present.
            if self.score_threshold is not None:
                score = r.get("score")
                distance = r.get("distance")
                if score is not None and score < self.score_threshold:
                    continue
                if distance is not None and (1 - distance) < self.score_threshold:
                    continue

            source = metadata.get("source")
            chunks.append(f"[Source: {source}]\n{text}" if source else text)

        return "\n\n---\n\n".join(chunks)

    # ------------------------------------------------------------------
    # Image helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _encode_image(image: Union[str, Path, bytes]) -> str:
        """
        Convert an image (file path or raw bytes) into a base64 data URL
        for the chat 'image_url' content block.
        """
        if isinstance(image, (str, Path)):
            path = Path(image)
            mime_type, _ = mimetypes.guess_type(path.name)
            mime_type = mime_type or "image/png"
            with open(path, "rb") as f:
                data = f.read()
        elif isinstance(image, bytes):
            mime_type = "image/png"
            data = image
        else:
            raise TypeError("image must be a file path (str/Path) or raw bytes")

        b64 = base64.b64encode(data).decode("utf-8")
        return f"data:{mime_type};base64,{b64}"

    # ------------------------------------------------------------------
    # Prompt building
    # ------------------------------------------------------------------
    @staticmethod
    def _build_prompt(query: str, context: str) -> str:
        if context.strip():
            return f"""You are a helpful AI assistant.

Use the following context to answer the question accurately.
If the context does not fully answer the question, you may supplement with your own knowledge, but prioritize the context.

Context:
{context}

Question:
{query}

Answer:"""
        return query

    # ------------------------------------------------------------------
    # Core generation
    # ------------------------------------------------------------------
    def generate_response(
        self,
        query: str,
        image: Optional[Union[str, Path, bytes]] = None,
        use_rag: bool = True,
        top_k: Optional[int] = None,
    ) -> str:
        """
        Generate a response, optionally grounded in retrieved context
        and/or conditioned on an image.

        Args:
            query: User question / instruction
            image: Optional path to an image file, or raw image bytes
            use_rag: If False, skips retrieval entirely (model-only)
            top_k: Override the default number of retrieved chunks

        Returns:
            Generated response text
        """
        context = self._retrieve_context(query, top_k=top_k) if use_rag else ""

        if use_rag:
            if context:
                print("[INFO] Relevant context found in FAISS — answering with RAG.")
            else:
                print("[INFO] No relevant context found — falling back to model's own knowledge.")

        prompt = self._build_prompt(query, context)

        if image is not None:
            image_url = self._encode_image(image)
            content = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}},
            ]
        else:
            content = prompt

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": content}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return response.choices[0].message.content

        except Exception as e:
            return f"Error generating response: {e}"

    def generate_response_simple(
        self, query: str, image: Optional[Union[str, Path, bytes]] = None
    ) -> str:
        """Generate a response with no RAG context (model-only), optionally with an image."""
        return self.generate_response(query, image=image, use_rag=False)

    def search_and_summarize(self, query: str, top_k: int = 5) -> str:
        """
        Matches your original RAGSearch.search_and_summarize() behavior,
        but now falls back to the model's own knowledge instead of
        returning a hardcoded "not found" string.
        """
        context = self._retrieve_context(query, top_k=top_k)

        if not context:
            print("[INFO] No relevant documents found — using model's own knowledge.")

        return self.generate_response(
            query=f"Summarize the information related to '{query}'.",
            use_rag=True,
            top_k=top_k,
        )


# -------------------------
# Example
# -------------------------

if __name__ == "__main__":

    chatbot = Gemma3RAGChatbot()

    # Original-style summarization (now with fallback instead of hard "not found")
    summary = chatbot.search_and_summarize("What is Attention Mechanism?", top_k=3)
    print(summary)

    # Direct Q&A with RAG + fallback
    print(chatbot.generate_response("What is attention is all you need"))

    # Image input
    print(chatbot.generate_response("Describe this figure.", image="diagram.png"))

    # Force model-only, skip retrieval
    print(chatbot.generate_response_simple("Tell me a joke"))