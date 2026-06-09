import os
import json
import logging
from typing import Dict, Any, List
from utils.charts import generate_matplotlib_chart
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)

def run_visualization_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Visualization Agent Node in LangGraph.
    Extracts key quantitative statistics, structures data, and generates charts.
    """
    topic = state.get("topic", "")
    insights = state.get("insights", {})
    insights_md = insights.get("markdown_insights", "")
    
    logger.info(f"Visualization Agent started for topic: '{topic}'")
    
    if not insights_md:
        logger.warning("No insights found to extract statistics from.")
        return {"statistics": [], "charts_data": []}
        
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY is not configured.")
        return {"error": "Google API key is missing."}
        
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1,
        google_api_key=api_key
    )
    
    prompt = f"""You are a Data Visualization Specialist. Your task is to identify and extract key numerical statistics and quantitative data from the following analysis of "{topic}".

ANALYSIS CONTENT:
{insights_md}

Using this data, you must design 2 or 3 distinct charts (e.g., bar chart, line chart, or pie chart) that illustrate the findings, and list 3-5 individual key statistics.
Respond ONLY with a valid JSON object matching the schema below. Do not wrap your response in markdown code blocks or add any comments.

JSON Schema:
{{
  "statistics": [
    {{
      "label": "Metric Description (e.g., Projected Healthcare Market Growth by 2030)",
      "value": "Value with unit (e.g., $188 Billion or 45%)"
    }}
  ],
  "charts": [
    {{
      "title": "Title of Chart (e.g., Adoption Rate by Sector)",
      "type": "bar", // MUST be either 'bar', 'line', or 'pie'
      "x_label": "Label for X axis (leave blank for pie)",
      "y_label": "Label for Y axis (leave blank for pie)",
      "labels": ["Label 1", "Label 2", "Label 3"], // X axis points or slice categories
      "values": [12.5, 45.2, 33.1] // Y axis numeric values or slice weights (MUST be float/int)
    }}
  ]
}}
"""
    
    try:
        response = llm.invoke([
            SystemMessage(content="You are an expert data analyst who outputs clean JSON conforming to strict schemas."),
            HumanMessage(content=prompt)
        ])
        
        # Clean response content (sometimes LLMs wrap JSON in ```json ... ```)
        cleaned_content = response.content.strip()
        if cleaned_content.startswith("```"):
            # Strip first line
            lines = cleaned_content.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned_content = "\n".join(lines).strip()
            
        data = json.loads(cleaned_content)
        
        extracted_stats = data.get("statistics", [])
        charts_list = data.get("charts", [])
        
        # Generate the static chart images for the PDF report
        # We save them in a temporary reports folder
        reports_dir = os.getenv("REPORTS_DIR", "reports")
        chart_paths = []
        
        for chart_def in charts_list:
            path = generate_matplotlib_chart(chart_def, output_dir=reports_dir)
            if path:
                chart_paths.append(path)
                
        logger.info(f"Visualization Agent finished. Extracted {len(extracted_stats)} stats and generated {len(chart_paths)} charts.")
        
        return {
            "statistics": extracted_stats,
            "charts_data": charts_list,
            "chart_paths": chart_paths
        }
        
    except Exception as e:
        logger.error(f"Error in Visualization Agent: {e}")
        # Return fallback empty structures
        return {
            "statistics": [
                {"label": "Data extraction error occurred", "value": "N/A"}
            ],
            "charts_data": [],
            "chart_paths": []
        }
