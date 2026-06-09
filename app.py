import os
import sys
import time
import requests
import threading
import streamlit as st
from utils.charts import create_plotly_figure

# ──────────────────────────────────────────────
# PAGE CONFIGURATION
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="TRACE Research Intelligence",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────
# BACKEND MANAGEMENT
# ──────────────────────────────────────────────

def start_backend_server():
    import uvicorn
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    uvicorn.run("backend.api:app", host="127.0.0.1", port=8000, log_level="error")

@st.cache_resource
def ensure_backend_active():
    backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
    try:
        response = requests.get(f"{backend_url}/docs", timeout=1)
        if response.status_code == 200:
            return backend_url
    except Exception:
        t = threading.Thread(target=start_backend_server, daemon=True)
        t.start()
        for _ in range(10):
            time.sleep(0.5)
            try:
                res = requests.get(f"{backend_url}/docs", timeout=0.5)
                if res.status_code == 200:
                    return backend_url
            except Exception:
                pass
    return backend_url

BACKEND_URL = ensure_backend_active()

# ──────────────────────────────────────────────
# GLOBAL CSS
# ──────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #050B18;
    color: #E8EDF5;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #080F22;
    border-right: 1px solid rgba(0, 212, 255, 0.15);
}
[data-testid="stSidebar"] * {
    color: #A0AEC0 !important;
}

/* ── Page header ── */
.nx-header {
    position: relative;
    padding: 2.5rem 0 2rem 0;
    margin-bottom: 2rem;
    border-bottom: 1px solid rgba(0, 212, 255, 0.12);
    overflow: hidden;
}
.nx-scan-line {
    position: absolute;
    bottom: 0;
    left: 0;
    height: 1px;
    width: 40%;
    background: linear-gradient(90deg, transparent, #00D4FF, transparent);
    animation: scan 3s ease-in-out infinite;
}
@keyframes scan {
    0%   { left: -40%; opacity: 0; }
    20%  { opacity: 1; }
    80%  { opacity: 1; }
    100% { left: 100%; opacity: 0; }
}
.nx-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #00D4FF;
    margin-bottom: 0.6rem;
}
.nx-title {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 3rem;
    line-height: 1.05;
    color: #E8EDF5;
    letter-spacing: 0.02em;
    margin: 0;
}
.nx-title span {
    color: #00D4FF;
}
.nx-subtitle {
    font-size: 0.95rem;
    color: #5A6A8A;
    margin-top: 0.5rem;
    font-weight: 400;
    letter-spacing: 0.01em;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid rgba(0, 212, 255, 0.12);
    gap: 0;
}
[data-testid="stTabs"] button[role="tab"] {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #5A6A8A;
    background: transparent;
    border: none;
    padding: 0.7rem 1.6rem;
    transition: color 0.2s ease;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #00D4FF;
    border-bottom: 2px solid #00D4FF;
    background: transparent;
}
[data-testid="stTabs"] button[role="tab"]:hover {
    color: #E8EDF5;
}

/* ── Panel cards ── */
.nx-panel {
    background: #0D1629;
    border: 1px solid rgba(0, 212, 255, 0.1);
    border-radius: 6px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.25rem;
    position: relative;
}
.nx-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, #00D4FF, #7B61FF);
    border-radius: 6px 0 0 6px;
}
.nx-panel-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #00D4FF;
    margin-bottom: 1rem;
}

/* ── Metric cards ── */
.nx-metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.nx-metric {
    background: #0D1629;
    border: 1px solid rgba(0, 212, 255, 0.1);
    border-radius: 6px;
    padding: 1.25rem 1.5rem;
    position: relative;
    overflow: hidden;
}
.nx-metric::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #00D4FF, #7B61FF);
}
.nx-metric-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #5A6A8A;
    margin-bottom: 0.5rem;
}
.nx-metric-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.9rem;
    font-weight: 700;
    color: #E8EDF5;
    line-height: 1;
}

/* ── Chat messages ── */
.nx-msg-user {
    background: #0D1629;
    border: 1px solid rgba(123, 97, 255, 0.25);
    border-radius: 6px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}
.nx-msg-user .nx-msg-role {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #7B61FF;
    margin-bottom: 0.5rem;
}
.nx-msg-assistant {
    background: #080F22;
    border: 1px solid rgba(0, 212, 255, 0.18);
    border-radius: 6px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}
.nx-msg-assistant .nx-msg-role {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #00D4FF;
    margin-bottom: 0.5rem;
}
.nx-msg-content {
    font-size: 0.9rem;
    line-height: 1.65;
    color: #C8D6E5;
}

/* ── Agent log ── */
.nx-log-item {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #5A6A8A;
    padding: 0.4rem 0;
    border-bottom: 1px solid rgba(0, 212, 255, 0.05);
    transition: color 0.3s ease;
}
.nx-log-item.active {
    color: #00D4FF;
}
.nx-log-item.done {
    color: #2DBD75;
}

/* ── Buttons ── */
div.stButton > button {
    background: transparent;
    color: #00D4FF;
    border: 1px solid rgba(0, 212, 255, 0.4);
    border-radius: 4px;
    padding: 0.65rem 2rem;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    font-size: 0.9rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}
div.stButton > button:hover {
    background: rgba(0, 212, 255, 0.08);
    border-color: #00D4FF;
    color: #E8EDF5;
}
div.stButton > button:active {
    background: rgba(0, 212, 255, 0.15);
}

/* ── Download button ── */
div.stDownloadButton > button {
    background: transparent;
    color: #7B61FF;
    border: 1px solid rgba(123, 97, 255, 0.4);
    border-radius: 4px;
    padding: 0.55rem 1.5rem;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    font-size: 0.85rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
div.stDownloadButton > button:hover {
    background: rgba(123, 97, 255, 0.08);
    border-color: #7B61FF;
    color: #E8EDF5;
}

/* ── Form inputs ── */
div[data-testid="stTextInput"] input {
    background: #0D1629;
    border: 1px solid rgba(0, 212, 255, 0.15);
    border-radius: 4px;
    color: #E8EDF5;
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    padding: 0.6rem 1rem;
}
div[data-testid="stTextInput"] input:focus {
    border-color: rgba(0, 212, 255, 0.5);
    box-shadow: 0 0 0 1px rgba(0, 212, 255, 0.15);
}
div[data-testid="stTextInput"] input::placeholder {
    color: #3A4A6A;
}
div[data-testid="stTextInput"] label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #5A6A8A;
}

/* ── Select sliders ── */
div[data-testid="stSlider"] label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #5A6A8A;
}

/* ── Expanders ── */
details > summary {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #5A6A8A;
}
details[open] > summary {
    color: #00D4FF;
}
details {
    background: #080F22;
    border: 1px solid rgba(0, 212, 255, 0.08);
    border-radius: 4px;
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
}

/* ── Info / Error / Success alerts ── */
div[data-testid="stAlert"] {
    background: #0D1629;
    border-radius: 4px;
    border: 1px solid rgba(0, 212, 255, 0.15);
    font-size: 0.88rem;
    color: #A0AEC0;
}

/* ── Markdown body text ── */
.stMarkdown p, .stMarkdown li {
    font-size: 0.92rem;
    line-height: 1.7;
    color: #8A9ABB;
}
.stMarkdown h2, .stMarkdown h3 {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    letter-spacing: 0.05em;
    color: #C8D6E5;
}

/* ── Chat input ── */
div[data-testid="stChatInput"] textarea {
    background: #0D1629;
    border: 1px solid rgba(0, 212, 255, 0.15);
    color: #E8EDF5;
    font-family: 'Inter', sans-serif;
    font-size: 0.88rem;
    border-radius: 4px;
}

/* ── Sidebar specific ── */
[data-testid="stSidebar"] .nx-sidebar-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #3A4A6A !important;
    margin-bottom: 0.4rem;
    display: block;
}
[data-testid="stSidebar"] .nx-sidebar-step {
    font-family: 'Inter', sans-serif;
    font-size: 0.82rem;
    color: #5A6A8A !important;
    padding: 0.3rem 0;
    border-bottom: 1px solid rgba(0, 212, 255, 0.05);
}
[data-testid="stSidebar"] .nx-sidebar-step span {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #00D4FF !important;
    margin-right: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────

if "report_data" not in st.session_state:
    st.session_state.report_data = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_topic" not in st.session_state:
    st.session_state.last_topic = ""

# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────

with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div style="font-family: 'Rajdhani', sans-serif; font-size: 1.3rem; font-weight: 700;
                letter-spacing: 0.1em; color: #E8EDF5; margin-bottom: 0.3rem;">
        TRACE
    </div>
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.6rem; letter-spacing: 0.18em;
                color: #00D4FF; text-transform: uppercase; margin-bottom: 2rem;">
        Research Intelligence v1.0
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<span class="nx-sidebar-label">Environment</span>', unsafe_allow_html=True)
    st.info("Set GOOGLE_API_KEY and TAVILY_API_KEY in your .env file before running.")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<span class="nx-sidebar-label">Workflow</span>', unsafe_allow_html=True)
    steps_sidebar = [
        ("01", "Enter a research topic"),
        ("02", "Select research depth"),
        ("03", "Run the agent pipeline"),
        ("04", "Review the results dashboard"),
        ("05", "Ask questions in RAG chat"),
    ]
    for code, label in steps_sidebar:
        st.markdown(
            f'<div class="nx-sidebar-step"><span>{code}</span>{label}</div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.6rem;
                letter-spacing: 0.1em; color: #2A3A5A; text-transform: uppercase;">
        Powered by Gemini and LangGraph
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────
# PAGE HEADER
# ──────────────────────────────────────────────

st.markdown("""
<div class="nx-header">
    <div class="nx-eyebrow">Multi-Agent Research Intelligence Platform</div>
    <div class="nx-title">TRACE <span>Research</span></div>
    <div class="nx-subtitle">Autonomous agent pipeline — web retrieval, fact-checking, RAG synthesis</div>
    <div class="nx-scan-line"></div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# TABS
# ──────────────────────────────────────────────

tab_generate, tab_dashboard, tab_chat = st.tabs([
    "Research Station",
    "Results Dashboard",
    "RAG Chat"
])

# ──────────────────────────────────────────────
# TAB 1 — RESEARCH STATION
# ──────────────────────────────────────────────

with tab_generate:
    st.markdown("""
    <div style="font-family: 'Rajdhani', sans-serif; font-size: 1.4rem; font-weight: 600;
                letter-spacing: 0.05em; color: #C8D6E5; margin-bottom: 1.5rem;">
        Initiate Research Run
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        topic_input = st.text_input(
            "Research Topic",
            placeholder="e.g., Future of AI in Healthcare, Renewable Energy in India",
            help="Enter a topic or question for the agents to investigate comprehensively.",
            label_visibility="visible"
        )

    with col2:
        depth = st.select_slider(
            "Depth",
            options=["Brief", "Detailed", "Exhaustive"],
            value="Detailed",
            help="Brief: 2 sources. Detailed: 3 sources. Exhaustive: 5 sources plus full scraping."
        )

    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button("Run Agent Pipeline", use_container_width=True)

    if generate_btn:
        if not topic_input.strip():
            st.error("A research topic is required to proceed.")
        else:
            agent_steps = [
                ("INIT",       "Initializing multi-agent state machine"),
                ("RETRIEVAL",  "Research agent — querying Tavily and scraping web sources"),
                ("VERIFY",     "Fact-checker agent — running source consistency verification"),
                ("ANALYSIS",   "Analyst agent — extracting insights, challenges, and trends"),
                ("VISUALIZE",  "Visualization agent — indexing statistics and drafting charts"),
                ("WRITE",      "Writer agent — assembling report document"),
                ("INDEX",      "Finalizing — saving outputs and indexing in ChromaDB"),
            ]

            st.markdown('<div class="nx-panel"><div class="nx-panel-title">Agent Pipeline — Live Log</div>', unsafe_allow_html=True)
            log_slots = []
            for tag, desc in agent_steps:
                slot = st.empty()
                slot.markdown(
                    f'<div class="nx-log-item"><span style="color:#2A3A5A;margin-right:0.75rem;">{tag}</span>{desc}</div>',
                    unsafe_allow_html=True
                )
                log_slots.append((slot, tag, desc))
            st.markdown("</div>", unsafe_allow_html=True)

            # Animate steps and call backend
            with st.spinner(""):
                payload = {"topic": topic_input, "depth": depth.lower()}

                for i, (slot, tag, desc) in enumerate(log_slots[:-1]):
                    slot.markdown(
                        f'<div class="nx-log-item active"><span style="margin-right:0.75rem;">{tag}</span>{desc}</div>',
                        unsafe_allow_html=True
                    )
                    time.sleep(1.5)
                    slot.markdown(
                        f'<div class="nx-log-item done"><span style="margin-right:0.75rem;">{tag}</span>{desc}</div>',
                        unsafe_allow_html=True
                    )

                try:
                    res = requests.post(f"{BACKEND_URL}/api/research", json=payload, timeout=300)
                    if res.status_code == 200:
                        st.session_state.report_data = res.json()
                        st.session_state.last_topic = topic_input
                        st.session_state.chat_history = []

                        last_slot, last_tag, last_desc = log_slots[-1]
                        last_slot.markdown(
                            f'<div class="nx-log-item done"><span style="margin-right:0.75rem;">{last_tag}</span>{last_desc}</div>',
                            unsafe_allow_html=True
                        )
                        st.success(f"Pipeline complete — report ready for '{topic_input}'")
                    else:
                        st.error(f"Pipeline failed: {res.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Could not reach backend API: {e}")

# ──────────────────────────────────────────────
# TAB 2 — RESULTS DASHBOARD
# ──────────────────────────────────────────────

with tab_dashboard:
    if st.session_state.report_data is None:
        st.markdown("""
        <div class="nx-panel" style="text-align:center; padding: 3rem;">
            <div style="font-family:'Rajdhani',sans-serif; font-size:1rem; letter-spacing:0.1em;
                        text-transform:uppercase; color:#2A3A5A; margin-bottom:0.75rem;">
                No report loaded
            </div>
            <div style="font-size:0.85rem; color:#3A4A6A;">
                Run the agent pipeline in Research Station to populate this view.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        report = st.session_state.report_data

        # Report header + download
        c_title, c_dl = st.columns([4, 1])
        with c_title:
            st.markdown(f"""
            <div style="font-family:'Rajdhani',sans-serif; font-size:1.6rem; font-weight:700;
                        letter-spacing:0.04em; color:#C8D6E5; margin-bottom:0.25rem;">
                {report.get("topic", "Research Report")}
            </div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                        letter-spacing:0.12em; text-transform:uppercase; color:#2A3A5A;">
                Analysis complete — all agents resolved
            </div>
            """, unsafe_allow_html=True)
        with c_dl:
            dl_url = f"{BACKEND_URL}/api/download_pdf?topic={requests.utils.quote(report.get('topic', ''))}"
            try:
                pdf_res = requests.get(dl_url)
                if pdf_res.status_code == 200:
                    st.download_button(
                        label="Download PDF",
                        data=pdf_res.content,
                        file_name=f"{report.get('topic', 'report').replace(' ', '_').lower()}_report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.warning("PDF is still compiling or failed.")
            except Exception as e:
                st.error(f"PDF download unavailable: {e}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Metrics
        stats = report.get("statistics", [])
        if stats:
            st.markdown("""
            <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                        letter-spacing:0.14em; text-transform:uppercase; color:#3A4A6A;
                        margin-bottom:0.75rem;">
                Key Data Points
            </div>
            """, unsafe_allow_html=True)
            cols = st.columns(min(len(stats), 4))
            for idx, col in enumerate(cols):
                if idx < len(stats):
                    with col:
                        label_text = stats[idx].get("label", "")[:45]
                        value_text = stats[idx].get("value", "")
                        st.markdown(f"""
                        <div class="nx-metric">
                            <div class="nx-metric-label">{label_text}</div>
                            <div class="nx-metric-value">{value_text}</div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("No numerical metrics were extracted from this research.")

        # Charts
        charts = report.get("charts_data", [])
        if charts:
            st.markdown("""
            <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                        letter-spacing:0.14em; text-transform:uppercase; color:#3A4A6A;
                        margin-bottom:0.75rem; margin-top:1.5rem;">
                Insight Charts
            </div>
            """, unsafe_allow_html=True)
            c_cols = st.columns(len(charts))
            for idx, c_col in enumerate(c_cols):
                with c_col:
                    fig = create_plotly_figure(charts[idx])
                    # Apply dark theme overrides
                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="#0D1629",
                        font=dict(color="#8A9ABB", family="Inter"),
                        xaxis=dict(gridcolor="rgba(0,212,255,0.06)", color="#5A6A8A"),
                        yaxis=dict(gridcolor="rgba(0,212,255,0.06)", color="#5A6A8A"),
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No chart data was generated for this report.")

        st.markdown("<br>", unsafe_allow_html=True)

        # Fact-check log
        with st.expander("Source Verification and Fact-Checking Log"):
            fact_text = report.get("fact_check_results", "No fact-checking details available.")
            st.markdown(f"""
            <div style="font-family:'JetBrains Mono',monospace; font-size:0.78rem;
                        line-height:1.8; color:#5A6A8A; white-space:pre-wrap;">
{fact_text}
            </div>
            """, unsafe_allow_html=True)

        # References
        with st.expander("Reference Bibliography"):
            sources = report.get("sources", [])
            if sources:
                for idx, src in enumerate(sources):
                    st.markdown(f"""
                    <div style="margin-bottom:0.75rem;">
                        <span style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                                     color:#00D4FF; margin-right:0.5rem;">[{idx + 1}]</span>
                        <a href="{src.get('url','#')}" target="_blank"
                           style="color:#C8D6E5; font-size:0.88rem; text-decoration:none;
                                  border-bottom:1px solid rgba(0,212,255,0.2);">
                            {src.get('title', 'Untitled')}
                        </a>
                        <div style="font-size:0.78rem; color:#3A4A6A; margin-top:0.25rem;
                                    padding-left:1.5rem;">
                            {src.get('snippet', '')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No references were recorded for this report.")

        # Full report
        st.markdown("""
        <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                    letter-spacing:0.14em; text-transform:uppercase; color:#3A4A6A;
                    margin-bottom:0.75rem; margin-top:1.5rem;">
            Full Report
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="nx-panel" style="padding:2rem 2.25rem;">
            <div style="font-size:0.9rem; line-height:1.85; color:#8A9ABB;">
                {report.get("report", "")}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ──────────────────────────────────────────────
# TAB 3 — RAG CHAT
# ──────────────────────────────────────────────

with tab_chat:
    if st.session_state.report_data is None:
        st.markdown("""
        <div class="nx-panel" style="text-align:center; padding: 3rem;">
            <div style="font-family:'Rajdhani',sans-serif; font-size:1rem; letter-spacing:0.1em;
                        text-transform:uppercase; color:#2A3A5A; margin-bottom:0.75rem;">
                RAG index not initialized
            </div>
            <div style="font-size:0.85rem; color:#3A4A6A;">
                Generate a report in Research Station to unlock the chat interface.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        active_topic = st.session_state.report_data.get("topic", "")
        st.markdown(f"""
        <div style="margin-bottom:1.5rem;">
            <div style="font-family:'Rajdhani',sans-serif; font-size:1.4rem; font-weight:700;
                        letter-spacing:0.04em; color:#C8D6E5;">
                {active_topic}
            </div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                        letter-spacing:0.12em; text-transform:uppercase; color:#2A3A5A;">
                Ask questions — answers are cited from the research vector index
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Render history
        for msg in st.session_state.chat_history:
            role = msg["role"]
            content = msg["content"]
            sources = msg.get("sources", [])

            if role == "user":
                st.markdown(f"""
                <div class="nx-msg-user">
                    <div class="nx-msg-role">You</div>
                    <div class="nx-msg-content">{content}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="nx-msg-assistant">
                    <div class="nx-msg-role">Nexus Assistant</div>
                    <div class="nx-msg-content">{content}</div>
                </div>
                """, unsafe_allow_html=True)

                if sources:
                    with st.expander("View Citations"):
                        for src in sources:
                            idx_src = src.get("index", "")
                            title = src.get("title", "")
                            url = src.get("url", "#")
                            st.markdown(
                                f'<a href="{url}" target="_blank" style="font-size:0.82rem; '
                                f'color:#7B61FF; text-decoration:none;">[{idx_src}] {title}</a>',
                                unsafe_allow_html=True
                            )

        # Chat input
        chat_query = st.chat_input("Enter your question about the research...")

        if chat_query:
            st.session_state.chat_history.append({"role": "user", "content": chat_query})
            st.rerun()

    # Trigger API call if last message is from user
    if (
        st.session_state.report_data is not None
        and st.session_state.chat_history
        and st.session_state.chat_history[-1]["role"] == "user"
    ):
        user_query = st.session_state.chat_history[-1]["content"]
        active_topic = st.session_state.report_data.get("topic", "")

        with st.spinner("Retrieving relevant context and generating answer..."):
            try:
                chat_payload = {"topic": active_topic, "query": user_query}
                res = requests.post(f"{BACKEND_URL}/api/chat", json=chat_payload, timeout=60)
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": data.get("answer", ""),
                        "sources": data.get("sources", [])
                    })
                    st.rerun()
                else:
                    st.error("RAG query failed — the backend returned an error.")
            except Exception as e:
                st.error(f"Could not reach the RAG assistant: {e}")