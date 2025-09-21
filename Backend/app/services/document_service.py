import google.generativeai as genai
from dotenv import load_dotenv
import os
import tempfile
from pathlib import Path
from typing import Dict
from fastapi import UploadFile
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()

class State(TypedDict):
    file_path: str
    content: str
    category: str

class DocumentService:
    """Service for handling document upload and processing - exact same logic as retrievel.py"""
    
    def __init__(self):
        # Configure Gemini AI with actual API key
        self.api_key = os.getenv('GEMINI_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.client = genai
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            self.ai_enabled = True
        else:
            print("⚠️ GEMINI_API_KEY not found - using mock AI responses")
            self.model = None
            self.ai_enabled = False
        
        # Create the workflow graph - exact same as original
        self.graph = StateGraph(State)
        self.graph.add_node("load_doc", self.load_doc)
        self.graph.add_node("decision", self.decision)
        self.graph.add_node("embed_and_store", self.embed_and_store)
        
        self.graph.set_entry_point("load_doc")
        self.graph.add_edge("load_doc", "decision")
        self.graph.add_edge("decision", "embed_and_store")
        self.graph.add_edge("embed_and_store", END)
        
        self.app = self.graph.compile()
    
    async def process_uploaded_file(self, file: UploadFile) -> Dict[str, str]:
        """
        Process an uploaded file using the exact same workflow as retrievel.py
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Initialize state
            initial_state: State = {
                "file_path": temp_file_path,
                "content": "",
                "category": ""
            }
            
            # Process through the graph workflow
            final_state = self.app.invoke(initial_state)
            
            return {
                "file_path": temp_file_path,
                "content_length": len(final_state["content"]),
                "category": final_state["category"],
                "status": "success"
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    def load_doc(self, state: State):
        """Load document - exact same logic as original load_doc function"""
        file_path = state["file_path"]
        ext = Path(file_path).suffix.lower()
        if ext == ".pdf":
            loader = PyPDFLoader(file_path=file_path)
            docs = loader.load()
            text = " ".join([d.page_content for d in docs])

        elif ext == ".txt":
            loader = TextLoader(file_path)
            docs = loader.load()
            text = " ".join([d.page_content for d in docs])
        else:
            raise ValueError(f"Unsupported file type: {ext}")
        
        return {"file_path": file_path, "content": text, "category": ""}

    def decision(self, state: State):
        """Document categorization - exact same logic as original decision function"""
        prompt = f"""You are a professional leader document classifier.
        check the document loaded by user belong to which category.
        For example:
        when user upload document related to  :
           - employment_contract.txt
           - service_agreement.txt
           - nda.txt
           - rent_agreement.txt
           
           then it's document category is contracts.
           
        when user upload documents related to :
        
           - refund_policy.txt
           - privacy_policy.txt
           - terms_and_conditions.txt
           - warranty_policy.txt
           
           then it's document category is policy.
           
           
        In the same why various documents will be uploaded . you will categorize them as contracts or policy.
        
        Document content to classify:
        {state['content'][:2000]}...
        """
        
        if self.ai_enabled and self.model:
            # Use the model directly, not client.models
            response = self.model.generate_content(prompt)
            category = response.candidates[0].content.parts[0].text.strip().lower()
        else:
            # Mock AI response for testing
            content_lower = state['content'][:500].lower()
            if any(word in content_lower for word in ['contract', 'agreement', 'employment', 'service', 'nda', 'rent']):
                category = "contracts"
            elif any(word in content_lower for word in ['policy', 'refund', 'privacy', 'terms', 'warranty']):
                category = "policy"
            else:
                category = "contracts"  # default fallback
        
        if "contract" in category:
            category = "contracts"
        elif "policy" in category:
            category = "policy"
        else:
            category = "unknown"

        return {"file_path": state["file_path"], "content": state["content"], "category": category}
        
    def embed_and_store(self, state: State):
        """Embed and store - exact same logic as original embed_and_store function"""
        if self.ai_enabled and self.api_key:
            try:
                # Pass API key explicitly to avoid credential issues
                embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/embedding-001",
                    google_api_key=self.api_key
                )
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)

                # Split the loaded text into documents
                split_docs = text_splitter.create_documents([state["content"]])

                # Create or append to collection dynamically using category name
                vector_store = QdrantVectorStore.from_documents(
                    documents=split_docs,
                    url="http://localhost:6333",
                    collection_name=state["category"],  # "contracts" or "policy"
                    embedding=embeddings,
                    force_recreate=False  # don't overwrite old data
                )
                print(f"✅ Document successfully stored in '{state['category']}' collection")
            except Exception as e:
                print(f"⚠️ Vector storage failed: {e}")
                print("📝 Document processed but not stored in vector DB")
        else:
            print("📝 AI disabled - document processed but not stored in vector DB")

        return state