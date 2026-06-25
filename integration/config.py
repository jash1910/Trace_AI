import os

# Base Directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PV_REPO_PATH = os.path.join(BASE_DIR, "PrivateVault.ai-main")

# Output Files
LEDGER_PATH = os.path.join(BASE_DIR, "pv_audit_ledger.jsonl")
REPORT_PATH = os.path.join(BASE_DIR, "benchmark_report.json")

# Agents list
TRACE_AGENTS = [
    "research_agent",
    "fact_checker_agent",
    "analyst_agent",
    "visualization_agent",
    "writer_agent",
]
