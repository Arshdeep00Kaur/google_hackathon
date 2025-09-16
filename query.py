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
    You are a highly knowledgeable AI assistant.

    Your task:
    - Answer the user’s question strictly using the provided context.
    - Do not use outside knowledge or guess beyond the context.
    - Always include page numbers when giving an answer.
    - Write the response in a clear, well-structured, and professional manner.
    - If the context does not contain enough information, say:
    "The provided documents do not contain sufficient information to answer this query."

    Format your answer like this:

    Answer:
    <your explanation in 2-3 short paragraphs>

    Reference:
    - Page <page_number_1> → short summary of relevant content
    - Page <page_number_2> → short summary of relevant content

    Context:
    {context}

    User Question:
    {query}
    """
    response = client.models.generate_content(
    model="gemini-1.5-flash",   # or gemini-1.5-pro if you want higher quality
    contents=[
        {"role": "system", "parts": [{"text": system_prompt}]},
        {"role": "user", "parts": [{"text": query}]}
    ]
    )

    return response.candidates[0].content.parts[0].text
    