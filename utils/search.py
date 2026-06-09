import os
import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load env variables
load_dotenv()

logger = logging.getLogger(__name__)

def search_tavily(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the web using Tavily API.
    Returns a list of dicts with keys: 'title', 'url', 'snippet'
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        logger.warning("TAVILY_API_KEY environment variable not found. Returning empty search results.")
        return []
    
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "max_results": max_results,
        "search_depth": "advanced"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        
        sources = []
        for r in results:
            sources.append({
                "title": r.get("title", "Untitled"),
                "url": r.get("url", ""),
                "snippet": r.get("content", "")
            })
        return sources
    except Exception as e:
        logger.error(f"Error calling Tavily Search API: {e}")
        return []

def scrape_url(url: str, timeout: int = 10) -> str:
    """
    Scrape a webpage and return cleaned, readable paragraph texts joined together.
    """
    if not url:
        return ""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
            
        # Extract paragraph text
        paragraphs = soup.find_all('p')
        text_blocks = [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 20]
        
        # Join content
        text = "\n\n".join(text_blocks)
        
        # Truncate content to keep it reasonable (e.g. 8000 characters)
        if len(text) > 8000:
            text = text[:8000] + "\n\n[Content truncated for length...]"
            
        return text
    except Exception as e:
        logger.warning(f"Failed to scrape webpage at {url}: {e}")
        return ""
