from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
import google.generativeai as genai
import os
from typing import Dict

# Load environment variables
load_dotenv()

class QueryService:
    """Service implementing exact user_query function logic from GenrativeAICode/query.py"""
    
    def __init__(self):
        # EXACT same initialization as query.py
        self.api_key = os.getenv('GEMINI_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)  # Fixed: use actual API key instead of hardcoded
            self.client = genai
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            self.ai_enabled = True
        else:
            print("⚠️ GEMINI_API_KEY not found - using mock AI responses")
            self.model = None
            self.ai_enabled = False
    
    def user_query(self, query: str, category: str = "category") -> Dict:
        """
        EXACT implementation of user_query function from GenrativeAICode/query.py
        Only change: use actual API key and parameterized category
        """
        if self.ai_enabled and self.api_key:
            try:
                embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/embedding-001",
                    google_api_key=self.api_key
                )
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
                split_docs = text_splitter.create_documents(["content"])

                # Create or append to collection dynamically using category name
                vector_store = QdrantVectorStore.from_existing_collection(
                    url="http://localhost:6333",
                    collection_name=category,  # "contracts" or "policy" or "category"
                    embedding=embeddings
                )
                search_results = vector_store.similarity_search(
                    query=query,
                    k=5  # Limit to top 5 results
                )
                print(f"✅ Found {len(search_results)} relevant documents in vector DB")
                
                # Create context from search results
                context = "\n\n".join([
                    f"Page Number: {result.metadata.get('page', 'N/A')}\n"
                    f"File Location: {result.metadata.get('source', 'N/A')}\n"
                    f"Page Content:\n{result.page_content}"
                    for result in search_results
                ])
                
            except Exception as e:
                print(f"⚠️ Vector search failed: {e}")
                context = "No relevant documents found in vector store."
        else:
            print("📝 AI disabled - using mock context")
            context = f"Mock context for query about '{query}' in category '{category}'"

        # EXACT same system prompt - DO NOT CHANGE
        system_prompt = f"""
    You are an AI legal assistant that helps users understand complex legal documents.

    Your responsibilities:
    - Read the provided context (retrieved legal document chunks).
    - Simplify the content into clear, accessible language without losing legal meaning.
    - Provide accurate, practical guidance so that users can make informed decisions.
    - Always include page numbers and file references when possible so the user can verify.
    - If the answer is not present in the provided context, say:
    "I could not find specific information about this in the provided documents."
    - Do NOT invent or assume legal advice beyond the given context.

    Context:
    {context}

    User Question: {query}

    Please provide a simplified, user-friendly answer with page references.
    """
        
        if self.ai_enabled and self.model:
            # Use the model directly, not client.models
            response = self.model.generate_content(system_prompt)
            ai_response = response.candidates[0].content.parts[0].text
        else:
            # Mock AI response for testing
            ai_response = f"Mock response for query: '{query}'. AI service is not available. This would normally provide legal analysis based on uploaded documents in the '{category}' category."
        
        return {
            "query": query,
            "response": ai_response,
            "found_documents": len(search_results)
        }