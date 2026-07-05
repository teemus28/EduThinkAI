from data_loader import load_all_documents
from embedding import EmbeddingPipeline
from vector_store import FaissVectorStore
from search import Gemma3RAGChatbot

if __name__=='__main__':

    chatbot = Gemma3RAGChatbot()

    # Original-style summarization (now with fallback instead of hard "not found")
    # summary = chatbot.search_and_summarize("What is Attention Mechanism?", top_k=3)
    # print(summary)

    # Direct Q&A with RAG + fallback
    # print(chatbot.generate_response("Describe laws of motion??"))

    # Image input
    print(chatbot.generate_response("Describe this image.", image="page1.jpg"))
    
    # docs = load_all_documents("pdf_files")
    # store = FaissVectorStore("faiss_store")
    # store.build_from_documents(docs)
    # store.load()
    # print(store.query("Describe laws of motion??", top_k=3))
    
    