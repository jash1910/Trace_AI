import os
import logging
from typing import Dict, Any, List
from utils.search import search_tavily, scrape_url
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)

def run_research_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Research Agent Node in LangGraph.
    Generates search queries, searches the web, fetches content, and cleans sources.
    """
    topic = state.get("topic", "")
    depth = state.get("depth", "detailed").lower()
    
    logger.info(f"Research Agent started for topic: '{topic}' with depth: '{depth}'")
    
    # 1. Determine number of search queries and results based on depth
    max_queries = 3
    results_per_query = 3
    if depth == "brief":
        max_queries = 2
        results_per_query = 2
    elif depth == "exhaustive":
        max_queries = 5
        results_per_query = 4
        
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY is not configured.")
        return {"error": "Google API key is missing."}
        
    # 2. Formulate search queries using Gemini
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        google_api_key=api_key
    )
    
    query_prompt = f"""You are a research director. The user wants to write a comprehensive research report on: "{topic}".
Generate {max_queries} distinct, highly specific search queries that will yield high-quality academic papers, market analysis, reports, or expert articles on this topic.
Format the output as a simple list with one query per line, and absolutely nothing else. Do not number them or add bullet points.
"""
    
    try:
        response = llm.invoke([
            SystemMessage(content="You are a helpful research query generator."),
            HumanMessage(content=query_prompt)
        ])
        
        queries = [q.strip() for q in response.content.strip().split("\n") if q.strip()]
        # Fallback if parsing fails or returns garbage
        if not queries:
            queries = [topic, f"{topic} trends", f"{topic} market analysis"]
            
        queries = queries[:max_queries]
        logger.info(f"Generated search queries: {queries}")
        
    except Exception as e:
        logger.error(f"Error generating search queries: {e}")
        queries = [topic]
        
    # 3. Execute searches & collect URLs
    raw_sources = {}
    for q in queries:
        logger.info(f"Searching for: '{q}'")
        search_results = search_tavily(q, max_results=results_per_query)
        for res in search_results:
            url = res.get("url")
            if url and url not in raw_sources:
                raw_sources[url] = {
                    "title": res.get("title", "Untitled"),
                    "url": url,
                    "snippet": res.get("snippet", ""),
                    "content": ""
                }
                
    # Convert to list
    collected_sources = list(raw_sources.values())
    logger.info(f"Collected {len(collected_sources)} unique source URLs.")
    
    # 4. Scrape full content for top sources to ensure rich context
    # We scrape up to a limit based on depth to keep runtime reasonable
    scrape_limit = 4
    if depth == "brief":
        scrape_limit = 2
    elif depth == "exhaustive":
        scrape_limit = 8
        
    scraped_count = 0
    for src in collected_sources:
        if scraped_count >= scrape_limit:
            break
            
        url = src.get("url")
        logger.info(f"Scraping text from: {url}")
        content = scrape_url(url)
        if content:
            src["content"] = content
            scraped_count += 1
            
    # Filter out sources that have neither a snippet nor content
    final_sources = [s for s in collected_sources if s.get("snippet") or s.get("content")]
    
    logger.info(f"Research Agent finished. Kept {len(final_sources)} sources with content.")
    
    return {
        "sources": final_sources
    }
