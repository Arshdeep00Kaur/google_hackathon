import google.generativeai as genai
from dotenv import load_dotenv
import os 
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv()
api_key=os.getenv('GEMINI_API_KEY')
genai.configure(api_key="YOUR_GOOGLE_API_KEY")
client = genai
model = genai.GenerativeModel("gemini-1.5-flash")


class State(TypedDict):
    file_path:str
    content:str
    category:str 
    
def load_doc(state:State):
    file_path=state["file_path"]
    ext=Path(file_path).suffix.lower()
    if ext==".pdf":
        loader=PyPDFLoader(file_path=file_path)
        docs=loader.load()
        text = " ".join([d.page_content for d in docs])

    elif ext == ".txt":
        loader = TextLoader(file_path)
        docs = loader.load()
        text = " ".join([d.page_content for d in docs])
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    
    return {"file_path": file_path, "content": text, "category": ""}
        

    

def decision(state:State):
    prompt="""You are a professional leader document classifier.
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
            """
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
    )
    
    category = response.candidates[0].content.parts[0].text.strip().lower()
    if "contract" in category:
        category = "contracts"
    elif "policy" in category:
        category = "policy"
    else:
        category = "unknown"

    return {"file_path": state["file_path"], "content": state["content"], "category": category}
    
    
def embed_and_store(state: State):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
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

    return state

graph = StateGraph(State)
graph.add_node("load_doc", load_doc)
graph.add_node("decision", decision)
graph.add_node("embed_and_store", embed_and_store)

graph.set_entry_point("load_doc")
graph.add_edge("load_doc", "decision")
graph.add_edge("decision", "embed_and_store")
graph.add_edge("embed_and_store", END)

app = graph.compile()