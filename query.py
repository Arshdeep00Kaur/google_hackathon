from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
import google.generativeai as genai
import os 
load_dotenv()
api_key=os.getenv('GEMINI_API_KEY')
genai.configure(api_key="YOUR_GOOGLE_API_KEY")
client = genai

def user_query(query):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
    split_docs = text_splitter.create_documents(["content"])

    # Create or append to collection dynamically using category name
    vector_store = QdrantVectorStore.from_existing_collection(
        documents=split_docs,
        url="http://localhost:6333",
        collection_name="category",  # "contracts" or "policy"
        embedding=embeddings,
        force_recreate=False  # don't overwrite old data
    )
    search_results = vector_store.similarity_search(
        query=query,
        k=5  # Limit to top 3 results
    )
    print(f"Found {len(search_results)} relevant documents")
     # Create context from search results
    context = "\n\n".join([
        f"Page Number: {result.metadata.get('page', 'N/A')}\n"
        f"File Location: {result.metadata.get('source', 'N/A')}\n"
        f"Page Content:\n{result.page_content}"
        for result in search_results
        ])

    
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
    response = client.models.generate_content(
    model="gemini-1.5-flash",   # or gemini-1.5-pro if you want higher quality
    contents=[
        {"role": "system", "parts": [{"text": system_prompt}]},
        {"role": "user", "parts": [{"text": query}]}
    ]
    )

    return response.candidates[0].content.parts[0].text
    