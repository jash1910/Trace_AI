# AI-Powered Autonomous Research Assistant 🔬

An advanced, full-stack, autonomous research platform that generates publication-grade intelligence reports from any user-provided topic. The platform utilizes a multi-agent LangGraph workflow, structures analytics, generates custom interactive charts, compiles printable PDF reports, and indexes research sources into a ChromaDB vector database for RAG-powered citations chat Q&A.

---

## Architecture Flow

```mermaid
graph TD
    User([User Input: Topic & Depth]) --> Streamlit[Streamlit Frontend Dashboard]
    Streamlit -->|HTTP POST /api/research| FastAPI[FastAPI Backend]
    FastAPI -->|Trigger Workflow| LangGraphWorkflow[LangGraph Workflow]
    
    subgraph Multi-Agent System (LangGraph)
        LangGraphWorkflow --> ResearchAgent[Research Agent]
        ResearchAgent -->|Tavily Search & Web Scraper| WebSources[(Cleaned Web Corpus)]
        WebSources --> FactCheckerAgent[Fact Checker Agent]
        FactCheckerAgent -->|Cross-referencing & Verification Log| AnalystAgent[Analyst Agent]
        AnalystAgent -->|Key Insights, Trends, SWOT| VisualizationAgent[Visualization Agent]
        VisualizationAgent -->|Extract Statistics & Plot Configs| WriterAgent[Writer Agent]
        WriterAgent -->|Generate Markdown Report| FinalState[Final State Compiled]
    end

    FinalState -->|Chunk & Index| ChromaDB[(Chroma Vector DB)]
    FinalState -->|Plot Matplotlib PNGs| Matplotlib[Matplotlib PNG Charts]
    FinalState -->|Compile Report + Charts| ReportLab[ReportLab PDF Compiler]
    
    ReportLab -->|Saved PDF| ReportsDir[reports/ directory]
    FastAPI -->|JSON Payload with Plotly Config| Streamlit
    Streamlit -->|Render Interactive Plotly Charts| UI[Premium UI Dashboard]

    UserChat([User Q&A Query]) --> ChatInterface[Chat Tab]
    ChatInterface -->|HTTP POST /api/chat| FastAPI
    FastAPI -->|Query Embeddings| GeminiEmbeddings[Gemini models/embedding-001]
    GeminiEmbeddings -->|Semantic Retrieval| ChromaDB
    ChromaDB -->|Context + Citation Metadata| RAGContext[Context Data]
    RAGContext -->|Synthesize Cited Answer| GeminiLLM[Gemini 1.5 Flash]
    GeminiLLM -->|Formatted Answer with [1][2]| ChatInterface
```

---

## Key Features

1. **Multi-Agent Orchestration**: Powered by LangGraph, coordinating 5 distinct agents:
   - **Research Agent**: Query generator and Tavily searcher that fetches full webpages and extracts clean paragraphs with BeautifulSoup.
   - **Fact Checker Agent**: Cross-references collected facts to flag conflicting numbers, claims, or inconsistencies.
   - **Analyst Agent**: Extracts key insights, trend forecasting, opportunities, and strategic risks.
   - **Visualization Agent**: Automatically parses quantitative statistics and configures double-format plots.
   - **Writer Agent**: Assembles final academic-style reports containing formal bibliographic listings.
2. **Interactive Dashboard**: A custom-themed Streamlit layout styling glassmorphic cards, gradient headings, Outfit typography, and responsive grid layouts.
3. **High-Fidelity PDF Generation**: ReportLab compiler featuring custom cover pages, running headers, confidentiality footers, auto-calculated page counts, and embedded charts.
4. **Dual Chart Engine**: Generates interactive Plotly charts for web dashboard rendering and exports Matplotlib static PNGs for PDF compilation.
5. **RAG Conversational Chat**: Stores research indices in ChromaDB to answer follow-up queries with clickable inline URL citations.

---

## Directory Structure

```
autonomous_research_assistant/
│
├── app.py                     # Streamlit frontend dashboard (runs FastAPI in background if inactive)
├── requirements.txt           # Python library dependencies
├── README.md                  # Project documentation & user manuals
├── .env.example               # Template for API credentials and local variables
│
├── agents/                    # LangGraph workflow nodes
│   ├── research_agent.py      # LLM query generator and web scraper
│   ├── fact_checker_agent.py  # Source discrepancy identifier
│   ├── analyst_agent.py       # Insight, trend, and strategic SWOT parser
│   ├── visualization_agent.py # Statistics compiler and chart trigger
│   └── writer_agent.py        # Report markdown writer and citation compiler
│
├── backend/
│   └── api.py                 # FastAPI endpoints (orchestrates LangGraph & downloads)
│
└── utils/
    ├── search.py              # Tavily API connections and BS4 text scrapers
    ├── rag.py                 # ChromaDB vector store builders and citation Q&A routers
    ├── pdf_generator.py       # ReportLab PDF builders and markdown text parsers
    └── charts.py              # Plotly JSON wrappers & Matplotlib plotting routines
```

---

## Setup & Local Installation

### Prerequisites
- Python 3.9+ installed on your local computer.
- A **Google Gemini API Key** (Get it at [Google AI Studio](https://aistudio.google.com/)).
- A **Tavily API Key** (Get it at [Tavily AI Search Engine](https://tavily.com/)).

### Installation Steps
1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd research_assistant
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in the root directory:
   ```bash
   cp .env.example .env
   ```
   Open the `.env` file and replace the placeholders with your API keys:
   ```env
   GOOGLE_API_KEY=AIzaSy...
   TAVILY_API_KEY=tvly-...
   ```

---

## How to Run Locally

Start the Streamlit application directly:
```bash
streamlit run app.py
```
> **Note**: During startup, `app.py` checks if the FastAPI backend server is active on `http://127.0.0.1:8000`. If it's not, it programmatically launches the backend in a daemon thread, so you only need to run a single command to start the entire system!

Access the dashboard in your web browser at `http://localhost:8501`.

---

## Deployment Guide

### Deploying on Streamlit Cloud
1. Push this repository to your GitHub account.
2. Log in to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Click **New app**, select your repository, branch, and specify `app.py` as the main entry point.
4. Click **Advanced settings...** and paste your API keys in the **Secrets** box:
   ```toml
   GOOGLE_API_KEY = "AIzaSy..."
   TAVILY_API_KEY = "tvly-..."
   ```
5. Click **Deploy**.

### Deploying on Render (Monorepo Setup)
Render can run the FastAPI backend and Streamlit frontend. For a single-instance deploy of the frontend (which runs the backend in a background process):
1. Connect your GitHub repository to [Render](https://render.com/).
2. Create a new **Web Service**.
3. Configure the following settings:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
4. Under **Environment Variables**, add:
   - `GOOGLE_API_KEY`
   - `TAVILY_API_KEY`
5. Deploy the service.
