import logging
from typing import Dict, Any, List
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END

# Import actual agents
from agents.research_agent import run_research_agent
from agents.fact_checker_agent import run_fact_checker_agent
from agents.analyst_agent import run_analyst_agent
from agents.visualization_agent import run_visualization_agent
from agents.writer_agent import run_writer_agent

# Import PrivateVault bridge
from integration.pv_bridge import PVCoordinator

logger = logging.getLogger("backend.workflow")

class ResearchState(TypedDict, total=False):
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
    pv_coordinator: Any
    pv_blocked: bool
    pv_reason: str
    _pv: Dict[str, Any]
    _pv_report: Dict[str, Any]

def _run_node(agent_fn, agent_id: str, state: ResearchState) -> ResearchState:
    """Helper to conditionally run agent execution through PVCoordinator if active."""
    # Check if pipeline has been blocked by PrivateVault in a preceding step
    if state.get("pv_blocked"):
        logger.info(f"[{agent_id}] Bypassing node because pipeline is blocked.")
        return state
        
    coordinator = state.get("pv_coordinator")
    if coordinator is not None:
        logger.info(f"[{agent_id}] Running execution through PVCoordinator.wrap_agent().")
        return coordinator.wrap_agent(agent_fn, agent_id, state)
    else:
        logger.info(f"[{agent_id}] Running direct execution.")
        delta = agent_fn(state)
        return {**state, **delta}

def research_node(state: ResearchState) -> ResearchState:
    return _run_node(run_research_agent, "research_agent", state)

def fact_checker_node(state: ResearchState) -> ResearchState:
    return _run_node(run_fact_checker_agent, "fact_checker_agent", state)

def analyst_node(state: ResearchState) -> ResearchState:
    return _run_node(run_analyst_agent, "analyst_agent", state)

def visualization_node(state: ResearchState) -> ResearchState:
    return _run_node(run_visualization_agent, "visualization_agent", state)

def writer_node(state: ResearchState) -> ResearchState:
    return _run_node(run_writer_agent, "writer_agent", state)

# Define StateGraph workflow
workflow = StateGraph(ResearchState)

# Add Node mapping
workflow.add_node("research", research_node)
workflow.add_node("fact_checker", fact_checker_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("visualization", visualization_node)
workflow.add_node("writer", writer_node)

# Setup graph edges/transitions
workflow.set_entry_point("research")
workflow.add_edge("research", "fact_checker")
workflow.add_edge("fact_checker", "analyst")
workflow.add_edge("analyst", "visualization")
workflow.add_edge("visualization", "writer")
workflow.add_edge("writer", END)

# Compile LangGraph
graph_runnable = workflow.compile()


# ──────────────────────────────────────────────
# Exported functions
# ──────────────────────────────────────────────

def run_trace(topic: str, depth: str = "detailed") -> Dict[str, Any]:
    """Runs TRACE normally without PrivateVault safety checks."""
    initial_state: ResearchState = {
        "topic": topic,
        "depth": depth,
        "sources": [],
        "fact_check_results": "",
        "insights": {},
        "statistics": [],
        "charts_data": [],
        "chart_paths": [],
        "report": "",
        "pdf_path": "",
        "error": "",
        "pv_coordinator": None,
        "pv_blocked": False,
        "pv_reason": ""
    }
    return graph_runnable.invoke(initial_state)

def run_trace_with_pv(topic: str, depth: str = "detailed") -> Dict[str, Any]:
    """Runs TRACE multi-agent flow secured with PrivateVault coordination trace."""
    coordinator = PVCoordinator(topic=topic)
    coordinator.start()
    
    initial_state: ResearchState = {
        "topic": topic,
        "depth": depth,
        "sources": [],
        "fact_check_results": "",
        "insights": {},
        "statistics": [],
        "charts_data": [],
        "chart_paths": [],
        "report": "",
        "pdf_path": "",
        "error": "",
        "pv_coordinator": coordinator,
        "pv_blocked": False,
        "pv_reason": ""
    }
    
    final_state = graph_runnable.invoke(initial_state)
    report = coordinator.finish()
    
    # Attach safety report
    final_state["_pv_report"] = report
    return final_state
