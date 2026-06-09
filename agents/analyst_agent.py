import os
import logging
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)

def run_analyst_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyst Agent Node in LangGraph.
    Extracts key insights, trends, opportunities, and challenges.
    """
    topic = state.get("topic", "")
    sources = state.get("sources", [])
    fact_check = state.get("fact_check_results", "")
    
    logger.info(f"Analyst Agent started for topic: '{topic}'")
    
    if not sources:
        logger.warning("No sources to analyze.")
        return {"insights": {}}
        
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY is not configured.")
        return {"error": "Google API key is missing."}
        
    # Format source text for the LLM
    source_texts = []
    for idx, src in enumerate(sources):
        title = src.get("title", "Untitled")
        body = src.get("content", "")
        if not body:
            body = src.get("snippet", "")
            
        body_snippet = body[:1500] if body else "No content available."
        source_texts.append(f"Source [{idx + 1}]: {title}\nContent: {body_snippet}\n---")
        
    sources_formatted = "\n\n".join(source_texts)
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,
        google_api_key=api_key
    )
    
    prompt = f"""You are a senior Industry Analyst. Your goal is to analyze the research sources and the verification report to extract key insights, major trends, opportunities, and challenges/risks for the research topic: "{topic}".

SOURCES:
{sources_formatted}

FACT CHECKING RESULTS:
{fact_check}

Your output MUST be a structured analysis. Provide a highly professional, comprehensive breakdown detailing:
1. **Key Insights**: What are the most critical takeaways from the collected research?
2. **Major Industry Trends**: What direction is the field moving in? (Provide 3-5 distinct trends with data/context).
3. **Strategic Opportunities**: What are the primary opportunities for development, growth, or innovation?
4. **Challenges, Risks, and Barriers**: What are the primary risks, roadblocks, or challenges?

Output the analysis in clean Markdown structure.
"""
    
    try:
        response = llm.invoke([
            SystemMessage(content="You are a brilliant industry analyst, market advisor, and researcher."),
            HumanMessage(content=prompt)
        ])
        
        insights_md = response.content
        logger.info("Analyst Agent finished successfully.")
        
        # We store the resulting markdown analysis
        return {
            "insights": {
                "markdown_insights": insights_md
            }
        }
    except Exception as e:
        logger.error(f"Error in Analyst Agent: {e}")
        return {
            "insights": {
                "error": f"Analysis process encountered an error: {e}"
            }
        }
