"""
app.py — AI Knowledge Hub · Chat page
"""
import streamlit as st
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="AI Knowledge Hub",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #f8f6f1; color: #1a1a1a; }
/* Hide Streamlit's auto-generated page nav */
[data-testid="stSidebarNav"] { display: none !important; }


/* ── Sidebar ── */
[data-testid="stSidebar"] { background: #1a1a1a !important; }
[data-testid="stSidebar"] * { color: #f8f6f1 !important; }
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #2a2a2a !important;
    border-color: #444 !important;
    color: #f8f6f1 !important;
}
[data-testid="stSidebar"] input {
    background: #2a2a2a !important;
    color: #f8f6f1 !important;
    border-color: #444 !important;
}
[data-testid="stSidebar"] input::placeholder { color: #666 !important; }

/* Sidebar brand */
.sidebar-brand {
    font-family: 'DM Mono', monospace;
    font-size: 18px;
    font-weight: 500;
    color: #f8f6f1;
    letter-spacing: -0.5px;
    padding: 4px 0 16px 0;
    border-bottom: 1px solid #333;
    margin-bottom: 8px;
}

/* Nav menu items */
.nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 12px;
    border-radius: 8px;
    font-size: 13px;
    font-family: 'DM Mono', monospace;
    color: #aaa;
    cursor: pointer;
    margin: 2px 0;
    transition: background 0.15s;
}
.nav-item.active {
    background: #2a2a2a;
    color: #f8f6f1;
}
.sidebar-section {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #555 !important;
    padding: 16px 0 6px 0;
    border-bottom: 1px solid #333;
    margin-bottom: 8px;
}

/* ── Chat ── */
.hub-title {
    font-family: 'DM Mono', monospace;
    font-size: 26px;
    font-weight: 500;
    letter-spacing: -1px;
    border-bottom: 2px solid #1a1a1a;
    padding-bottom: 10px;
    margin-bottom: 4px;
}
.hub-sub {
    font-size: 12px;
    color: #888;
    margin-bottom: 24px;
    font-family: 'DM Mono', monospace;
}
.user-msg {
    background: #1a1a1a;
    color: #f8f6f1;
    border-radius: 16px 16px 4px 16px;
    padding: 12px 16px;
    margin: 8px 0;
    max-width: 68%;
    margin-left: auto;
    font-size: 14px;
    line-height: 1.6;
}
.ai-msg {
    background: white;
    border: 1px solid #e5e0d8;
    border-left: 3px solid #c8a96e;
    border-radius: 4px 16px 16px 16px;
    padding: 14px 18px;
    margin: 8px 0;
    max-width: 90%;
    font-size: 14px;
    line-height: 1.8;
    white-space: pre-wrap;
}
.msg-meta {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #999;
    margin-top: 4px;
}
.source-tag {
    display: inline-block;
    background: #f0ebe3;
    border: 1px solid #d4cfc8;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 10px;
    font-family: 'DM Mono', monospace;
    color: #666;
    margin: 2px;
}
.sql-tag {
    display: inline-block;
    background: #e8f4e8;
    border: 1px solid #b8d4b8;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 10px;
    font-family: 'DM Mono', monospace;
    color: #2d6a2d;
    margin: 2px;
}
.model-pill {
    display: inline-block;
    background: #1a1a1a;
    color: #c8a96e;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 10px;
    font-family: 'DM Mono', monospace;
    margin-bottom: 12px;
}
.stButton > button {
    background: #1a1a1a !important;
    color: #f8f6f1 !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
}
.stButton > button:hover { background: #333 !important; }
[data-testid="stTextInput"] input {
    background: white !important;
    color: #1a1a1a !important;
    border: 1px solid #e5e0d8 !important;
    border-radius: 8px !important;
}
.suggestion-link {
    display: block;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #4a9edd !important;
    cursor: pointer;
    padding: 2px 0;
    margin: 1px 0;
    text-decoration: underline;
    background: none;
    border: none;
}
[data-testid="stSidebar"] button[kind="tertiary"] {
    background: none !important;
    border: none !important;
    color: #4a9edd !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    padding: 1px 0 !important;
    min-height: unset !important;
    height: auto !important;
    text-decoration: underline;
    text-align: left !important;
    justify-content: flex-start !important;
}
[data-testid="stTextInput"] input::placeholder { color: #aaa !important; }
</style>
""", unsafe_allow_html=True)

# ── Agent init ─────────────────────────────────────────────────────────────────
@st.cache_resource
def load_agent():
    from src.agents.knowledge_agent import KnowledgeAgent
    return KnowledgeAgent()

agent = load_agent()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:

    # Brand
    st.markdown('<div class="sidebar-brand">🧠 Knowledge Hub</div>', unsafe_allow_html=True)

    # Navigation links (visual only — Streamlit handles routing via pages/)
    st.markdown("""
    <div class="nav-item active">💬 &nbsp; Chat</div>
    """, unsafe_allow_html=True)
    st.page_link("pages/📊_Dashboard.py",      label="📊  Eval Dashboard")
    st.page_link("pages/🔀_Model_Comparator.py", label="🔀  Model Comparator")

    # Status
    ##st.markdown('<div class="sidebar-section">System</div>', unsafe_allow_html=True)
    ##try:
    ##    agent  = load_agent()
    ##    status = agent.status()
    ##    col1, col2 = st.columns(2)
    ##    with col1:
    ##        st.metric("Docs", status["documents_indexed"])
    ##    with col2:
    ##        st.metric("Tables", len(status["db_schema"].splitlines()))
    ##except Exception as e:
    ##    st.error(f"Agent error: {e}")

    # Model selector
    st.markdown('<div class="sidebar-section">Select Model</div>', unsafe_allow_html=True)
    PROVIDER_MODELS = {
        "groq":   ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"],
        "ollama": ["llama3.2", "mistral", "gemma2", "phi3"],
        "openai": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        "gemini": ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
    }
    selected_provider = st.selectbox(
        "Provider", list(PROVIDER_MODELS.keys()), index=0,
        key="chat_provider", label_visibility="collapsed",
    )
    selected_model = st.selectbox(
        "Model", PROVIDER_MODELS[selected_provider], index=0,
        key="chat_model", label_visibility="collapsed",
    )

    # Ingest
    st.markdown('<div class="sidebar-section">Ingest</div>', unsafe_allow_html=True)
    ingest_url = st.text_input("URL", placeholder="https://example.com/doc", label_visibility="collapsed")
    if st.button("+ Ingest URL", use_container_width=True):
        if ingest_url:
            with st.spinner("Ingesting..."):
                try:
                    n = agent.ingest(ingest_url)
                    st.success(f"✅ {n} chunks ingested")
                    st.cache_resource.clear()
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    uploaded = st.file_uploader("Upload PDF/TXT", type=["pdf", "txt"], label_visibility="collapsed")
    if uploaded and st.button("+ Ingest File", use_container_width=True):
        with st.spinner("Ingesting..."):
            try:
                import tempfile
                suffix = os.path.splitext(uploaded.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                    tmp_file.write(uploaded.read())
                    tmp_path = tmp_file.name
                n = agent.ingest(tmp_path)
                os.remove(tmp_path)
                st.success(f"✅ {n} chunks from {uploaded.name}")
                st.cache_resource.clear()
                st.rerun()
            except Exception as e:
                st.error(str(e))

    # Suggestions
    st.markdown('<div class="sidebar-section">Try these</div>', unsafe_allow_html=True)
    suggestions = [
        "What products do we have in stock?",
        "Which customers are from Bogotá?",
        "Total sales in Q1 2024?",
        "Show top selling products",
    ]
    for s in suggestions:
        if st.button(s, use_container_width=True, key=f"sug_{s[:20]}",
                     help=None, type="tertiary"):
            st.session_state["pending_query"] = s
            st.session_state["messages"].append({"role": "user", "content": s})
            count = int(st.session_state.get("input_key", "user_input_0").split("_")[-1]) + 1
            st.session_state["input_key"] = f"user_input_{count}"
            st.rerun()

    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()

    st.markdown("""
    <div style="font-size:10px; color:#444; text-align:center; padding-top:16px;">
    <a href="https://github.com/alexv6v6" style="color:#c8a96e; text-decoration:none;">github.com/alexv6v6</a>
    </div>
    """, unsafe_allow_html=True)

# ── Main ───────────────────────────────────────────────────────────────────────
st.markdown('<div class="hub-title">💬 Chat</div>', unsafe_allow_html=True)

provider = st.session_state.get("chat_provider", "groq")
model    = st.session_state.get("chat_model", "llama-3.3-70b-versatile")
st.markdown(f'<div class="model-pill">⚡ {provider} · {model}</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Render chat history
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        sources_html = ""
        for s in set(msg.get("sources", [])):
            if s:
                sources_html += f'<span class="source-tag">📄 {s.split("/")[-1] or s[:40]}</span>'
        if msg.get("sql"):
            sources_html += '<span class="sql-tag">🗄️ SQL</span>'
        st.markdown(f"""
        <div class="ai-msg">{msg["content"]}</div>
        <div class="msg-meta">{sources_html}</div>
        """, unsafe_allow_html=True)

# Empty state
if not st.session_state["messages"]:
    st.markdown("""
    <div style="text-align:center; padding:60px 20px;">
        <div style="font-size:48px; margin-bottom:14px;">🧠</div>
        <div style="font-family:'DM Mono',monospace; font-size:14px; color:#666;">
            Ask questions about your documents or database
        </div>
        <div style="font-size:12px; margin-top:8px; color:#aaa;">
            Use the sidebar to ingest PDFs, URLs, or try the suggestions
        </div>
    </div>
    """, unsafe_allow_html=True)

# Input bar
input_key  = st.session_state.get("input_key", "user_input_0")
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input(
        label="q", label_visibility="collapsed",
        placeholder="Ask anything about your documents or data...",
        value="", key=input_key,
    )
with col2:
    send = st.button("Ask →", use_container_width=True)

if send and user_input.strip():
    query = user_input.strip()
    st.session_state["messages"].append({"role": "user", "content": query})
    st.session_state["pending_query"] = query
    count = int(input_key.split("_")[-1]) + 1
    st.session_state["input_key"] = f"user_input_{count}"
    st.rerun()

if "pending_query" in st.session_state:
    query    = st.session_state.pop("pending_query")
    provider = st.session_state.get("chat_provider", "groq")
    model    = st.session_state.get("chat_model", "llama-3.3-70b-versatile")
    with st.spinner(f"🧠 {provider} / {model}..."):
        try:
            from src.llm.model_manager import ModelManager
            mm     = ModelManager(default_provider=provider, default_model=model)
            result = agent.ask(query, llm=mm)
            st.session_state["messages"].append({
                "role":    "assistant",
                "content": result["answer"],
                "sources": result.get("doc_sources", []),
                "sql":     result.get("sql_query"),
            })
            # Auto-evaluate (non-blocking)
            try:
                from src.prompts.evaluator import PromptEvaluator
                from src.dashboard.stats_service import log_query
                evaluator   = PromptEvaluator()
                context     = " ".join(result.get("doc_sources", [])) + str(result.get("sql_query", ""))
                eval_result = evaluator.evaluate(
                    question=query, response=result["answer"], context=context,
                    prompt_name="knowledge_agent_system", prompt_version="v2",
                )
                log_query(
                    question=query, answer=result["answer"],
                    query_type=result.get("query_type", "unknown"),
                    scores=eval_result.scores,
                    strengths=eval_result.strengths, weaknesses=eval_result.weaknesses,
                    sql_query=result.get("sql_query"), doc_sources=result.get("doc_sources", []),
                )
            except Exception:
                pass
        except Exception as e:
            st.session_state["messages"].append({
                "role": "assistant", "content": f"⚠️ Error: {str(e)}", "sources": [], "sql": None,
            })
    st.rerun()
