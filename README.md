# Google Hackathon Document Classifier

This project classifies documents (contracts, policies, etc.) using Google Gemini AI and stores embeddings in Qdrant for semantic search.

## Features
- PDF and TXT document loading
- Document classification (contracts, policy, etc.)
- Embedding generation with Gemini
- Vector storage and retrieval using Qdrant
- Graph-based workflow with LangGraph

## Setup
1. Clone the repository
2. Create a Python virtual environment and activate it
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set your Gemini API key in a `.env` file:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
5. Start Qdrant locally (default: http://localhost:6333)

## Usage
- Run `retrievel.py` to process and classify documents
- Run `query.py` to search and answer questions using stored embeddings

## Folder Structure
- `retrievel.py`: Document loading, classification, and embedding
- `query.py`: Semantic search and question answering
- `requirements.txt`: Python dependencies
- `README.md`: Project documentation

## License
MIT
