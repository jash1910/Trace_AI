import os
import logging
import shutil
from typing import List, Dict, Any
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

def get_db_path(topic: str) -> str:
    """
    Generate a clean folder name for storing Chroma DB files per topic.
    """
    safe_topic = "".join([c if c.isalnum() else "_" for c in topic]).strip("_").lower()
    db_base = os.getenv("DATABASE_DIR", "data/chroma")
    return os.path.join(db_base, safe_topic)

def initialize_vector_db(topic: str, report_content: str, sources: List[Dict[str, Any]]) -> bool:
    """
    Split the report and sources into chunks, embed them, and index in ChromaDB.
    """
    persist_dir = get_db_path(topic)
    
    # Clean previous database directory for this topic if it exists
    if os.path.exists(persist_dir):
        try:
            shutil.rmtree(persist_dir)
            logger.info(f"Cleaned existing ChromaDB directory at {persist_dir}")
        except Exception as e:
            logger.error(f"Failed to clear old database folder {persist_dir}: {e}")
            
    os.makedirs(persist_dir, exist_ok=True)
    
    documents = []
    
    # 1. Chunk and add the generated report
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    
    report_chunks = text_splitter.split_text(report_content)
    for i, chunk in enumerate(report_chunks):
        documents.append(Document(
            page_content=chunk,
            metadata={
                "source_title": "Generated Research Report",
                "source_url": "report",
                "source_index": "Report",
                "chunk_id": f"report_chunk_{i}"
            }
        ))
        
    # 2. Chunk and add the source references
    for idx, src in enumerate(sources):
        src_content = src.get("content", "")
        if not src_content:
            src_content = src.get("snippet", "") # Fallback to snippet
            
        if not src_content:
            continue
            
        src_chunks = text_splitter.split_text(src_content)
        for i, chunk in enumerate(src_chunks):
            documents.append(Document(
                page_content=chunk,
                metadata={
                    "source_title": src.get("title", "Untitled Source"),
                    "source_url": src.get("url", ""),
                    "source_index": f"[{idx + 1}]",
                    "chunk_id": f"source_{idx}_chunk_{i}"
                }
            ))
            
    if not documents:
        logger.warning("No documents found to index in vector database.")
        return False
        
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("GOOGLE_API_KEY environment variable is not set. Cannot initialize embeddings.")
            return False
            
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=api_key
        )
        
        # Save to Chroma DB
        Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=persist_dir
        )
        
        logger.info(f"Successfully indexed {len(documents)} document chunks in ChromaDB at {persist_dir}")
        return True
    except Exception as e:
        logger.error(f"Error initializing ChromaDB: {e}")
        return False

def answer_query(topic: str, query: str) -> Dict[str, Any]:
    """
    Retrieve contexts from ChromaDB and use Gemini to generate an answer with inline citations.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {
            "answer": "Error: GOOGLE_API_KEY is not configured.",
            "sources": []
        }
        
    persist_dir = get_db_path(topic)
    if not os.path.exists(persist_dir):
        return {
            "answer": f"No research database found for topic: '{topic}'. Please generate a report first.",
            "sources": []
        }
        
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=api_key
        )
        
        # Load Chroma DB
        db = Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings
        )
        
        # Retrieve relevant contexts
        retriever = db.as_retriever(search_kwargs={"k": 4})
        docs = retriever.invoke(query)
        
        # Assemble context string
        context_list = []
        citations_map = {}
        
        for doc in docs:
            idx = doc.metadata.get("source_index", "[Unknown]")
            title = doc.metadata.get("source_title", "Untitled Source")
            url = doc.metadata.get("source_url", "")
            
            # Map citations
            if idx not in citations_map and url != "report":
                citations_map[idx] = {"title": title, "url": url}
                
            context_list.append(f"Source: {idx} - {title}\nURL: {url}\nContent: {doc.page_content}\n---")
            
        context_str = "\n\n".join(context_list)
        
        # Generate Answer using LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.2,
            google_api_key=api_key
        )
        
        prompt = f"""You are a brilliant AI Research Assistant. Answer the user's question about '{topic}' based ONLY on the provided context below.

CONTEXT:
{context_str}

USER QUESTION:
{query}

INSTRUCTIONS:
1. Provide a direct, professional, and detailed answer.
2. You MUST include inline citations like [1], [2], etc., corresponding to the sources in the context that support your claims.
3. If the context does not contain enough information to answer the question, state that you do not have sufficient information in the collected research to answer, but still summarize whatever relevant points you can find.
4. Do NOT make up any citations or facts that are not present in the context.
"""
        
        response = llm.invoke(prompt)
        answer = response.content
        
        # Construct list of citations returned
        citations = []
        for key, val in citations_map.items():
            citations.append({
                "index": key,
                "title": val["title"],
                "url": val["url"]
            })
            
        # Sort citations by index
        citations.sort(key=lambda x: x["index"])
        
        return {
            "answer": answer,
            "sources": citations
        }
        
    except Exception as e:
        logger.error(f"Error querying RAG system: {e}")
        return {
            "answer": f"An error occurred while retrieving or processing your query: {e}",
            "sources": []
        }
