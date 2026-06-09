import os
import logging
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)

def run_writer_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Writer Agent Node in LangGraph.
    Assembles research materials and compiles a professional report in markdown.
    """
    topic = state.get("topic", "")
    sources = state.get("sources", [])
    fact_check = state.get("fact_check_results", "")
    insights = state.get("insights", {})
    insights_md = insights.get("markdown_insights", "")
    statistics = state.get("statistics", [])
    charts_data = state.get("charts_data", [])
    
    logger.info(f"Writer Agent started for topic: '{topic}'")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY is not configured.")
        return {"error": "Google API key is missing."}
        
    # 1. Format the references list for the prompt
    references_md = []
    for idx, src in enumerate(sources):
        title = src.get("title", "Untitled")
        url = src.get("url", "")
        references_md.append(f"[{idx + 1}] {title} - {url}")
        
    references_str = "\n".join(references_md)
    
    # 2. Format statistics & charts
    stats_str = ""
    for stat in statistics:
        stats_str += f"- **{stat.get('label')}**: {stat.get('value')}\n"
        
    charts_str = ""
    for idx, chart in enumerate(charts_data):
        charts_str += f"### Visualization {idx + 1}: {chart.get('title')}\n"
        charts_str += f"[Chart: {chart.get('title')} ({chart.get('type')})]\n\n"
        
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        google_api_key=api_key
    )
    
    prompt = f"""You are a Lead Research Writer. Your job is to compile the final professional Research Report on: "{topic}".

You have access to the following analytical materials:
- **Analyst Key Insights**:
{insights_md}

- **Fact Checking Log**:
{fact_check}

- **Extracted Statistics**:
{stats_str}

- **Extracted Chart Definitions**:
{charts_str}

- **Reference Sources**:
{references_str}

Write a comprehensive, professional, academic-grade research report. The report MUST follow this structure exactly:

# Research Report: {topic}

## 1. Executive Summary
Provide a high-level summary of the research topic, key findings, and strategic outlook. (At least 2 substantial paragraphs).

## 2. Introduction
Introduce the topic, scope of research, context, and why it is critical today.

## 3. Current Industry Overview
Explain the current state of the industry, technology, or field under research.

## 4. Major Trends
Elaborate on the key industry trends (3-5 trends) that are shaping the future, using quantitative statistics where possible.

## 5. Opportunities
Explain the strategic opportunities for growth, investment, or innovation.

## 6. Challenges and Risks
Detail the roadblocks, challenges, security, legal, ethical, or operational risks.

## 7. Future Outlook
Discuss what the next 5-10 years look like for this topic.

## 8. Key Statistics
Present the quantitative metrics in a clean, bulleted list:
{stats_str if stats_str else "No statistics extracted."}

## 9. Visualizations
Briefly explain each visualization and place the placeholder where the chart should be embedded:
{charts_str if charts_str else "No visualizations generated."}

## 10. References
Include the final list of references in the following format:
{references_str if references_str else "No references available."}

CRITICAL RULES:
1. You must integrate inline citations like [1], [2], etc. inside the text paragraphs when referring to facts, figures, or claims derived from specific sources.
2. The tone must be academic, formal, and authoritative. Do not use conversational language.
3. Write substantial paragraphs. Do not write short summaries. Make this a comprehensive report.
"""
    
    try:
        response = llm.invoke([
            SystemMessage(content="You are a professional technical writer and research compiler."),
            HumanMessage(content=prompt)
        ])
        
        report_md = response.content
        logger.info("Writer Agent finished successfully.")
        
        return {
            "report": report_md
        }
    except Exception as e:
        logger.error(f"Error in Writer Agent: {e}")
        return {
            "report": f"Writing process encountered an error: {e}"
        }
