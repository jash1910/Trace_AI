import os
import logging
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)

def run_fact_checker_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fact Checker Agent Node in LangGraph.
    Verifies consistency and detects conflicting claims across sources.
    """
    topic = state.get("topic", "")
    sources = state.get("sources", [])
    
    logger.info(f"Fact Checker Agent started for topic: '{topic}'")
    
    if not sources:
        logger.warning("No sources to check for contradictions.")
        return {"fact_check_results": "No source documents were retrieved for verification."}
        
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY is not configured.")
        return {"error": "Google API key is missing."}
        
    # Format source text for the LLM
    source_texts = []
    for idx, src in enumerate(sources):
        title = src.get("title", "Untitled")
        url = src.get("url", "")
        # Use content if available, fallback to snippet
        body = src.get("content", "")
        if not body:
            body = src.get("snippet", "")
        
        # Keep it concise to fit in token limit (e.g., first 1500 chars of each source)
        body_snippet = body[:1500] if body else "No content available."
        source_texts.append(f"Source [{idx + 1}]: {title}\nURL: {url}\nContent: {body_snippet}\n---")
        
    sources_formatted = "\n\n".join(source_texts)
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1,
        google_api_key=api_key
    )
    
    prompt = f"""You are a professional Fact-Checking and Verification Agent. Your task is to verify information consistency and detect conflicting claims across the following collected sources for the research topic: "{topic}".

SOURCES:
{sources_formatted}

Analyze the sources and produce a detailed Fact-Checking & Credibility Report.
Structure your report with the following headers:
1. **Source Reliability & Credibility Assessment**: Brief overview of the types of sources (e.g., news outlets, academic blogs, industry reports).
2. **Conflicting Claims & Contradictions**: Detail any contradictions in numbers, dates, claims, or future projections. If none are found, state "No major conflicting claims or contradictions detected."
3. **Consensus & Heavily Verified Facts**: Highlight points where multiple sources agree strongly.
4. **General Caveats & Missing Information**: Note any limitations in the sources.
"""
    
    try:
        response = llm.invoke([
            SystemMessage(content="You are an expert fact-checker and journalist."),
            HumanMessage(content=prompt)
        ])
        
        fact_check_log = response.content
        logger.info("Fact Checker Agent finished successfully.")
        return {
            "fact_check_results": fact_check_log
        }
    except Exception as e:
        logger.error(f"Error in Fact Checker Agent: {e}")
        return {
            "fact_check_results": f"Fact checking process encountered an error: {e}"
        }
