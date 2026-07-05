# 🎓 EduThinkAI – AI-Powered Educational Platform

> 🚀 **Live Demo:** [https://EduThinkAI.onrender.com](https://eduthinkai.onrender.com/)  

EduThinkAI is an AI-powered educational platform that helps students learn smarter through **Retrieval-Augmented Generation (RAG)** and **AI-generated Mind Maps**. It enables users to interact with educational documents, ask questions in natural language, analyze images, and visualize complex topics using interactive mind maps.

---

## ✨ Features

### 🤖 AI RAG Chatbot
- Chat with 100+ educational PDF documents
- Retrieval-Augmented Generation (RAG)
- FAISS vector search for semantic retrieval
- Hugging Face Gemma-3 integration
- Image understanding with multimodal support
- Context-aware responses with source retrieval

### 🧠 AI Mind Map Generator
- Generate interactive mind maps from:
  - 📄 PDF files
  - 🖼️ Images
  - 📑 Documents
- Hierarchical concept extraction
- Interactive HTML visualization
- Downloadable mind maps

### 💻 Modern User Interface
- Professional Streamlit frontend
- chatbot interface
- Light theme with intuitive navigation
- Toggle between Chatbot and Mind Map Generator
- Responsive design

---

# 🏗️ Project Architecture

```
                     EduThinkAI
                          │
          ┌───────────────┴───────────────┐
          │                               │
          ▼                               ▼
   🤖 AI Chatbot                  🧠 Mind Map Generator
          │                               │
          └───────────────┬───────────────┘
                          ▼
                   FastAPI Backend
                          │
          ┌───────────────┴───────────────┐
          │                               │
          ▼                               ▼
      FAISS Vector DB             Document Processing
          │
          ▼
 Sentence Transformers
          │
          ▼
 Hugging Face Gemma-3 API
```

---

# 🚀 Technologies Used

### Backend
- FastAPI
- Python
- LangChain
- FAISS
- Sentence Transformers
- Hugging Face Inference API
- PyMuPDF
- Pillow

### Frontend
- Streamlit
- HTML/CSS
- Requests

### AI Models
- Google Gemma-3-4B-IT
- all-MiniLM-L6-v2 Embeddings

---

# 📂 Project Structure

```
EduThinkAI
│
├── EduThinkAI/
│   ├── embedding.py
│   ├── vector_store.py
│   ├── search.py
│   ├── data_loader.py
│   ├── retriever.py
│   
│
├── extractor/
│
├── pdf_files/
│
├── faiss_store/
│   ├── faiss.index
│   └── metadata.pkl
│
├── uploads/
│
├── outputs/
│
├── frontend.py
│
├── combined_backend.py
│
├── requirements.txt
│
└── README.md
```

---

# 📚 How It Works

## 🤖 RAG Chatbot Workflow

```
User Query
      │
      ▼
Generate Embedding
      │
      ▼
FAISS Similarity Search
      │
      ▼
Retrieve Relevant Chunks
      │
      ▼
Gemma-3
      │
      ▼
Final AI Response
```

---

## 🧠 Mind Map Workflow

```
Upload Document
       │
       ▼
Text Extraction
       │
       ▼
AI Topic Detection
       │
       ▼
Tree Generation
       │
       ▼
Interactive HTML Mind Map
```

---

# ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/teemus28/EduThinkAI.git

cd EduThinkAI
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file

```env
HF_TOKEN=YOUR_HUGGINGFACE_TOKEN
```

---

# ▶️ Run the Backend

```bash
uvicorn backend:app --reload
```

Backend documentation

```
http://127.0.0.1:8000/docs
```

---

# ▶️ Run the Frontend

```bash
streamlit run frontend.py
```

---

# 📷 Supported Inputs

## Chatbot

- Text Queries
- Images

## Mind Map Generator

- PDF
- PNG
- JPG
- JPEG
- DOCX
- TXT

---

# 📈 Future Improvements

- User Authentication
- Chat History
- MongoDB Integration
- Cloud Vector Database
- Multi-document Chat
- Voice Input
- Quiz Generation
- Flashcard Generation
- Study Planner
- Learning Analytics
- PDF Upload from Frontend
- Multi-language Support

---

# 🎯 Applications

- 📖 Interactive Learning
- 🎓 Student Study Assistant
- 👨‍🏫 Teacher Content Preparation
- 📚 Research Assistance
- 📝 Exam Revision
- 🧠 Visual Knowledge Representation

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create your feature branch

```bash
git checkout -b feature/new-feature
```

3. Commit your changes

```bash
git commit -m "Add new feature"
```

4. Push the branch

```bash
git push origin feature/new-feature
```

5. Open a Pull Request

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**Sumeet Sahu**

- GitHub: https://github.com/teemus28

---

## ⭐ If you found this project useful, please consider giving it a star on GitHub!

