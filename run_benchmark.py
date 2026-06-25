"""
run_benchmark.py
================
TRACE multi-agent system benchmarking with PrivateVault security wrapping.
Runs the benchmark by executing the agents with and without PrivateVault.

Usage:
    python run_benchmark.py
"""

import os
import sys
from dotenv import load_dotenv

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Load environment variables
load_dotenv()

# Import actual agents
from agents.research_agent import run_research_agent
from agents.fact_checker_agent import run_fact_checker_agent
from agents.analyst_agent import run_analyst_agent
from agents.visualization_agent import run_visualization_agent
from agents.writer_agent import run_writer_agent

# Import benchmark execution orchestrator
from integration.benchmark_runner import execute_benchmark

def main():
    topic = "Future of Agentic AI Systems in Healthcare"
    
    # Run the benchmark suite using the actual agent functions
    execute_benchmark(
        research_agent_fn=run_research_agent,
        fact_checker_fn=run_fact_checker_agent,
        analyst_fn=run_analyst_agent,
        visualization_fn=run_visualization_agent,
        writer_fn=run_writer_agent,
        topic=topic
    )

if __name__ == "__main__":
    main()
