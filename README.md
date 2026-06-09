# TRACE

### Autonomous Research Intelligence Platform

**Research. Verify. Analyze. Generate.**

TRACE is an AI-powered autonomous research platform that transforms a single topic into a comprehensive, citation-backed research report within minutes.

Unlike traditional AI chatbots that generate responses from pre-trained knowledge, TRACE actively searches the web, gathers information from multiple sources, verifies claims, extracts insights, generates visualizations, creates professional reports, and allows users to interact with the collected knowledge through a Retrieval-Augmented Generation (RAG) chat system.

Built using a multi-agent architecture powered by LangGraph, TRACE automates the entire research workflow from information gathering to final report generation.

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

## Key Capabilities

### Real-Time Web Research

Collects information directly from live web sources rather than relying solely on LLM knowledge.

### Automated Fact Verification

Compares information across sources and identifies conflicting claims.

### Interactive Visualizations

Automatically converts extracted statistics into charts and graphs.

### Professional Report Generation

Creates detailed reports containing:

* Executive Summary
* Industry Overview
* Market Analysis
* Key Trends
* Opportunities
* Challenges
* Future Outlook
* Key Statistics
* Reference Bibliography

### RAG-Powered Research Chat

Ask questions about generated reports and receive citation-backed answers sourced directly from collected documents.

### PDF Export

Download professionally formatted research reports with references included.

---

## System Architecture

```text
User Topic Input
        │
        ▼
Research Agent
        │
        ▼
Fact Checker Agent
        │
        ▼
Analyst Agent
        │
        ▼
Visualization Agent
        │
        ▼
Writer Agent
        │
        ▼
Generated Report
        │
        ├── Interactive Charts
        ├── PDF Export
        └── Source References
                │
                ▼
          ChromaDB
                │
                ▼
          RAG Chat Interface
```

---

## Tech Stack

### Frontend

* Streamlit
* Plotly

### Backend

* FastAPI

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

### Environment Management

* Python
* dotenv

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
├── frontend/
│   ├── app.py
│
├── backend/
│   ├── main.py
│   ├── routes/
│   └── services/
│
├── agents/
│   ├── research_agent.py
│   ├── fact_checker_agent.py
│   ├── analyst_agent.py
│   ├── visualization_agent.py
│   └── writer_agent.py
│
├── rag/
│   ├── chroma_store.py
│   ├── embeddings.py
│   └── retrieval.py
│
├── reports/
│
├── charts/
│
├── data/
│
├── requirements.txt
│
├── .env
│
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
GEMINI_API_KEY=your_gemini_api_key

TAVILY_API_KEY=your_tavily_api_key
```

---

## Running the Application

### Start the Backend

```bash
uvicorn main:app --reload
```

### Launch the Frontend

```bash
streamlit run app.py
```

Open your browser and navigate to:

```text
http://localhost:8501
```

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

## Example Output

A completed TRACE report includes:

* Verified web sources
* Extracted key statistics
* Interactive charts
* Executive summary
* Market analysis
* Opportunities and risks
* Future outlook
* Source bibliography
* Downloadable PDF

---

## Why TRACE?

Traditional research requires:

* Searching dozens of websites
* Reading lengthy articles
* Organizing notes manually
* Verifying claims
* Creating visualizations
* Writing reports

TRACE automates this process through an intelligent multi-agent system that performs the entire workflow autonomously.

---

## Future Enhancements

* Multi-language research support
* PowerPoint generation
* Source credibility scoring
* Team collaboration features
* Research history tracking
* Cloud vector database support
* Scheduled automated research reports
* Enterprise deployment support

---

## Skills Demonstrated

This project showcases:

* Agentic AI Systems
* Multi-Agent Workflows
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
