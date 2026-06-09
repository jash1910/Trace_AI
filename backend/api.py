import os
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# LangGraph and Agents
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

from agents.research_agent import run_research_agent
from agents.fact_checker_agent import run_fact_checker_agent
from agents.analyst_agent import run_analyst_agent
from agents.visualization_agent import run_visualization_agent
from agents.writer_agent import run_writer_agent

# Utilities
from utils.pdf_generator import generate_pdf_report
from utils.rag import initialize_vector_db, answer_query

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("backend.api")

app = FastAPI(
    title="Autonomous Research Assistant API",
    description="Backend API serving Multi-Agent Workflows and RAG-based Chat Support",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- LANGGRAPH SETUP -----------------

class ResearchState(TypedDict):
    topic: str
    depth: str
    sources: List[Dict[str, Any]]
    fact_check_results: str
    insights: Dict[str, Any]
    statistics: List[Dict[str, Any]]
    charts_data: List[Dict[str, Any]]
    chart_paths: List[str]
    report: str
    pdf_path: str
    error: str

# Create StateGraph
workflow = StateGraph(ResearchState)

# Add Agent Nodes
workflow.add_node("research", run_research_agent)
workflow.add_node("fact_checker", run_fact_checker_agent)
workflow.add_node("analyst", run_analyst_agent)
workflow.add_node("visualization", run_visualization_agent)
workflow.add_node("writer", run_writer_agent)

# Define transitions
workflow.set_entry_point("research")
workflow.add_edge("research", "fact_checker")
workflow.add_edge("fact_checker", "analyst")
workflow.add_edge("analyst", "visualization")
workflow.add_edge("visualization", "writer")
workflow.add_edge("writer", END)

# Compile
graph_runnable = workflow.compile()

# ----------------- API SCHEMAS -----------------

class ResearchRequest(BaseModel):
    topic: str
    depth: str = "detailed" # brief, detailed, exhaustive

class ChatRequest(BaseModel):
    topic: str
    query: str

# Helper to generate safe filename
def get_safe_pdf_path(topic: str) -> str:
    safe_topic = "".join([c if c.isalnum() else "_" for c in topic]).strip("_").lower()
    reports_dir = os.getenv("REPORTS_DIR", "reports")
    return os.path.join(reports_dir, f"{safe_topic}_research_report.pdf")

# ----------------- API ENDPOINTS -----------------

@app.post("/api/research")
async def generate_report(req: ResearchRequest):
    """
    Triggers the multi-agent workflow to collect search results,
    run fact checking, perform analysis, extract statistics, and build a research report.
    """
    logger.info(f"Received research request for: '{req.topic}' (depth: {req.depth})")
    
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Research topic cannot be empty.")
        
    initial_state: ResearchState = {
        "topic": req.topic,
        "depth": req.depth,
        "sources": [],
        "fact_check_results": "",
        "insights": {},
        "statistics": [],
        "charts_data": [],
        "chart_paths": [],
        "report": "",
        "pdf_path": "",
        "error": ""
    }
    
    try:
        # Run the workflow
        result = graph_runnable.invoke(initial_state)
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
            
        report_content = result.get("report", "")
        sources = result.get("sources", [])
        chart_paths = result.get("chart_paths", [])
        
        # 1. Compile PDF Report
        pdf_path = get_safe_pdf_path(req.topic)
        generate_pdf_report(req.topic, report_content, chart_paths, pdf_path)
        
        # 2. Index Documents to Vector DB for QA Chat
        indexed_successfully = initialize_vector_db(req.topic, report_content, sources)
        if not indexed_successfully:
            logger.warning("RAG vector database initialization failed.")
            
        return {
            "topic": result.get("topic"),
            "report": report_content,
            "sources": sources,
            "fact_check_results": result.get("fact_check_results"),
            "statistics": result.get("statistics"),
            "charts_data": result.get("charts_data"),
            "pdf_path": pdf_path,
            "message": "Report and PDF generated successfully."
        }
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {e}")

@app.post("/api/chat")
async def chat_rag(req: ChatRequest):
    """
    Answers user query about the research database using RAG over indexed sources.
    """
    logger.info(f"Chat request for topic '{req.topic}': '{req.query}'")
    if not req.topic.strip() or not req.query.strip():
        raise HTTPException(status_code=400, detail="Topic and query cannot be empty.")
        
    res = answer_query(req.topic, req.query)
    return res

@app.get("/api/download_pdf")
async def download_pdf(topic: str = Query(..., description="The research topic for the PDF")):
    """
    Downloads the compiled PDF report for a given topic.
    """
    pdf_path = get_safe_pdf_path(topic)
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF report not found. Please generate it first.")
        
    safe_filename = "".join([c if c.isalnum() else "_" for c in topic]).strip("_").lower()
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"{safe_filename}_research_report.pdf"
    )

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("backend.api:app", host=host, port=port, reload=True)
