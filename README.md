# TRACE

### Autonomous Research Intelligence Platform

**Research. Verify. Analyze. Generate. Secure.**

TRACE is an AI-powered autonomous research platform that transforms a single topic into a comprehensive, citation-backed research report within minutes.

Unlike traditional AI chatbots that generate responses from pre-trained knowledge, TRACE actively searches the web, gathers information from multiple sources, verifies claims, extracts insights, generates visualizations, creates professional reports, and allows users to interact with the collected knowledge through a Retrieval-Augmented Generation (RAG) chat system.

Built using a multi-agent architecture powered by LangGraph, TRACE automates the entire research workflow from information gathering to final report generation.

This version of TRACE integrates the **PrivateVault** coordination framework to implement safety alignment, intent validation, and adversarial security benchmarking across all agent execution boundaries.

---

## Features

### Autonomous Research Pipeline

* Research any topic using real-time web search
* Gather and analyze information from multiple sources
* Eliminate duplicate sources automatically
* Generate structured research reports

### Multi-Agent Architecture

TRACE uses specialized AI agents that work together:

#### Research Agent

* Performs web searches
* Collects articles, blogs, reports, and research papers
* Aggregates source material

#### Fact Checker Agent

* Cross-verifies claims between sources
* Detects conflicting information
* Highlights inconsistencies for transparency

#### Analyst Agent

* Extracts key insights and trends
* Identifies opportunities and risks
* Summarizes critical findings

#### Visualization Agent

* Extracts numerical data and statistics
* Generates chart-ready datasets
* Creates interactive visualizations

#### Writer Agent

* Produces a complete research report
* Organizes findings into structured sections
* Includes citations and references

---

## PrivateVault Security & Alignment

TRACE wraps all agent execution boundaries with **PrivateVault** to enforce robust safety, intent validation, and data accountability checks:

1. **Intent Normalization**: Verifies that the agent's intent matches authorized system schemas.
2. **Risk Scoring**: Evaluates the potential risk level of requested actions before execution.
3. **Adversarial Stitching Detection**: Checks context windows and history for multi-turn prompt injection attacks.
4. **Rate-Limiting & Gatekeeping**: Prevents execution cascades and rate-limit violations.
5. **Decentralized Audit Logging**: Logs every agent action to a hash-chained, tamper-evident local ledger (`pv_audit_ledger.jsonl`).
6. **Merkle Proof Generation**: Computes a root cryptographic hash representing the complete session context history to guarantee lineage integrity.

---

## System Architecture

```text
User Topic Input
        │
        ▼
   [PrivateVault Coordinator] (Security Check: Intent, Risk, Injection Detection)
        │
        ▼
Research Agent
        │
        ▼
   [PrivateVault Coordinator]
        │
        ▼
Fact Checker Agent
        │
        ▼
   [PrivateVault Coordinator]
        │
        ▼
Analyst Agent
        │
        ▼
   [PrivateVault Coordinator]
        │
        ▼
Visualization Agent
        │
        ▼
   [PrivateVault Coordinator]
        │
        ▼
Writer Agent ──► Generated Report
                       │
                       ├── Interactive Charts
                       ├── PDF Export
                       └── Source References ──► ChromaDB ──► RAG Chat Interface
```

---

## Tech Stack

### Frontend

* Streamlit
* Plotly

### Backend

* FastAPI

### Security & Coordination

* PrivateVault Core

### AI Frameworks

* Google Gemini
* LangChain
* LangGraph

### Retrieval & Vector Storage

* ChromaDB

### Web Search

* Tavily Search API

### Data Processing

* Pandas
* NumPy

### Report Generation

* ReportLab

---

## Workflow

### Step 1: Research Collection

The user enters a research topic. The Research Agent generates search queries and gathers information from multiple web sources.

### Step 2: Fact Verification

The Fact Checker Agent compares findings across sources and identifies conflicting information.

### Step 3: Insight Analysis

The Analyst Agent extracts meaningful insights, trends, risks, and opportunities.

### Step 4: Data Visualization

The Visualization Agent identifies numerical information and converts it into visual charts.

### Step 5: Report Writing

The Writer Agent compiles all findings into a structured research document.

### Step 6: Knowledge Indexing

Documents are embedded and stored in ChromaDB for retrieval.

### Step 7: Conversational Research

Users can ask follow-up questions through the RAG-powered chat interface.

---

## Project Structure

```text
TRACE/
│
├── run_benchmark.py             # Root benchmark executor (actual agent imports)
├── benchmark_report.json        # Compiled comparative security and performance report
├── pv_audit_ledger.jsonl        # Cryptographically chained local decision ledger
│
├── integration/                 # PrivateVault integration layer
│   ├── __init__.py
│   ├── config.py                # Directories and output path configurations
│   ├── pv_bridge.py             # PVCoordinator wrapper & SDK fallback handlers
│   ├── attack_simulator.py      # Prompt Injection, Intent Drift, Unauthorized, Hidden Context simulators
│   ├── metrics.py               # Calculation utilities (consensus score, recovery rate, accuracy)
│   ├── benchmark_report.py      # JSON report compiler and ledger copy manager
│   └── helpers.py               # Workspace key validator
│
├── backend/
│   ├── api.py                   # REST API exposing /api/research with use_pv support
│   └── workflow.py              # Compiled LangGraph workflow with PV wrappers
│
├── agents/
│   ├── research_agent.py
│   ├── fact_checker_agent.py
│   ├── analyst_agent.py
│   ├── visualization_agent.py
│   └── writer_agent.py
│
├── reports/                     # ReportLab outputs & charts
├── data/                        # Vector DB storage
├── requirements.txt
├── .env
└── README.md
```

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/yourusername/trace.git

cd trace
```

### Create Virtual Environment

```bash
python -m venv venv
```

Activate the environment:

Mac/Linux

```bash
source venv/bin/activate
```

Windows

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY=your_gemini_api_key

TAVILY_API_KEY=your_tavily_api_key
```

---

## Running the Application

### Start the Application using Streamlit

The Streamlit app automatically boots and manages the backend API server. To launch the full interface:

```bash
venv/bin/streamlit run app.py
```

Open your browser and navigate to:

```text
http://localhost:8501
```

---

## Security & Performance Benchmarking

A comparative benchmarking framework tests the TRACE system **with and without** PrivateVault coordination. It automatically runs 4 attack vectors (Prompt Injection, Intent Drift, Unauthorized Action, Hidden Malicious Context) over a multi-turn workflow to evaluate the system's defenses.

To execute the benchmark suite:

```bash
venv/bin/python run_benchmark.py
```

This runs the benchmark and outputs:
1. **`benchmark_report.json`**: Performance metrics comparing consensus, speed, and safety block rates.
2. **`pv_audit_ledger.jsonl`**: The tamper-evident decision log.

---

## Example Research Topics

### Technology

* Future of AI in Healthcare
* Quantum Computing Trends
* Autonomous Vehicles

### Business

* Generative AI Market Analysis
* FinTech Industry Outlook
* E-Commerce Growth Forecast

### Sustainability

* Renewable Energy Adoption
* Green Hydrogen Economy
* Climate Technology Startups

### Cybersecurity

* Zero Trust Architecture
* AI-Powered Cybersecurity
* Banking Security Challenges

---

## Skills Demonstrated

This project showcases:

* Agentic AI Systems & Alignment
* Guardrails & Adversarial Defenses
* Tamper-Proof Lineage & Ledger Verification
* Multi-Agent Orchestration (LangGraph)
* Retrieval-Augmented Generation (RAG)
* Vector Databases
* Prompt Engineering
* LLM Orchestration
* Web Search Integration
* Data Visualization
* Backend API Development
* Full-Stack AI Engineering

---

## Author

### Jashvitha Lakshmi Omkaram

Computer Science Student specializing in AI, Data Science, and Intelligent Systems.

Passionate about building autonomous AI applications that automate complex workflows and transform information into actionable insights.

---

## License

This project is licensed under the MIT License.

Feel free to use, modify, and distribute this project for educational and research purposes.
