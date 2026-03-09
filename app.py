"""
app.py — Streamlit UI for AI Knowledge Hub
Hybrid RAG + SQL chat interface with document ingestion.
"""
import streamlit as st
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="AI Knowledge Hub",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp { background: #f8f6f1; color: #1a1a1a; }

[data-testid="stSidebar"] {
    background: #1a1a1a;
    color: #f8f6f1;
}
[data-testid="stSidebar"] * { color: #f8f6f1 !important; }

.hub-title {
    font-family: 'DM Mono', monospace;
    font-size: 28px;
    font-weight: 500;
    color: #1a1a1a;
    letter-spacing: -1px;
    border-bottom: 2px solid #1a1a1a;
    padding-bottom: 12px;
    margin-bottom: 8px;
}
.hub-sub {
    font-size: 13px;
    color: #666;
    margin-bottom: 28px;
    font-family: 'DM Mono', monospace;
}

.user-msg {
    background: #1a1a1a;
    color: #f8f6f1;
    border-radius: 16px 16px 4px 16px;
    padding: 14px 18px;
    margin: 8px 0;
    max-width: 70%;
    margin-left: auto;
    font-size: 14px;
    line-height: 1.6;
}
.ai-msg {
    background: white;
    border: 1px solid #e5e0d8;
    border-left: 3px solid #c8a96e;
    border-radius: 4px 16px 16px 16px;
    padding: 16px 20px;
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
    margin-top: 6px;
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
.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-family: 'DM Mono', monospace;
}
.badge-docs { background: #f0ebe3; color: #8b6914; border: 1px solid #d4b896; }
.badge-sql  { background: #e8f4e8; color: #2d6a2d; border: 1px solid #b8d4b8; }
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
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stTextInput"] input::placeholder {
    color: #aaa !important;
}
</style>
""", unsafe_allow_html=True)

# ── Agent init ─────────────────────────────────────────────────────────────────
@st.cache_resource
def load_agent():
    from src.agents.knowledge_agent import KnowledgeAgent
    return KnowledgeAgent()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧠 Knowledge Hub")
    st.markdown("---")

    # Status
    try:
        agent  = load_agent()
        status = agent.status()
        st.markdown(f"**📚 Docs indexed:** {status['documents_indexed']}")
        st.markdown(f"**🗄️ DB tables:** {len(status['db_schema'].splitlines())}")
    except Exception as e:
        st.error(f"Agent error: {e}")

    st.markdown("---")
    st.markdown("**📥 Ingest Document**")

    ingest_url = st.text_input("URL", placeholder="https://example.com/doc")
    if st.button("Ingest URL", use_container_width=True):
        if ingest_url:
            with st.spinner("Ingesting..."):
                try:
                    n = agent.ingest(ingest_url)
                    st.success(f"✅ {n} chunks ingested")
                    st.cache_resource.clear()
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    uploaded = st.file_uploader("Upload PDF/TXT", type=["pdf", "txt"])
    if uploaded and st.button("Ingest File", use_container_width=True):
        with st.spinner("Ingesting..."):
            try:
                import tempfile
                suffix = os.path.splitext(uploaded.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                    tmp_file.write(uploaded.read())
                    tmp_path = tmp_file.name
                n = agent.ingest(tmp_path)
                os.remove(tmp_path)
                st.success(f"✅ {n} chunks ingested from {uploaded.name}")
                st.cache_resource.clear()
                st.rerun()
            except Exception as e:
                st.error(str(e))

    st.markdown("---")
    st.markdown("**⚡ Try these:**")
    suggestions = [
        "What products do we have in stock?",
        "Which customers are from Bogotá?",
        "Total sales in Q1 2024?",
        "Show top selling products",
    ]
    for s in suggestions:
        if st.button(s, use_container_width=True):
            st.session_state["prefill"] = s

    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style="font-size:10px; color:#666; text-align:center;">
    Groq · ChromaDB · SQLite<br>
    <a href="https://github.com/alexv6v6" style="color:#c8a96e;">github.com/alexv6v6</a>
    </div>
    """, unsafe_allow_html=True)

# ── Main ───────────────────────────────────────────────────────────────────────
st.markdown('<div class="hub-title">AI Knowledge Hub</div>', unsafe_allow_html=True)
st.markdown('<div class="hub-sub">RAG · Text-to-SQL · Multi-source Knowledge</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Render chat
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        sources_html = ""
        if msg.get("sources"):
            for s in set(msg["sources"]):
                if s:
                    name = s.split("/")[-1] or s[:40]
                    sources_html += f'<span class="source-tag">📄 {name}</span>'
        if msg.get("sql"):
            sources_html += f'<span class="sql-tag">🗄️ SQL</span>'

        st.markdown(f"""
        <div class="ai-msg">{msg["content"]}</div>
        <div class="msg-meta">{sources_html}</div>
        """, unsafe_allow_html=True)

if not st.session_state["messages"]:
    st.markdown("""
    <div style="text-align:center; padding:60px 20px; color:#999;">
        <div style="font-size:48px; margin-bottom:16px;">🧠</div>
        <div style="font-family:'DM Mono',monospace; font-size:15px; color:#666;">
            Ask questions about your documents or database
        </div>
        <div style="font-size:12px; margin-top:8px; color:#999;">
            Ingest PDFs, URLs or query the SQL database directly
        </div>
    </div>
    """, unsafe_allow_html=True)

# Input
prefill = st.session_state.pop("prefill", "")
input_key = st.session_state.get("input_key", "user_input_0")
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input(
        label="q", label_visibility="collapsed",
        placeholder="Ask anything about your documents or data...",
        value=prefill, key=input_key,
    )
with col2:
    send = st.button("Ask →", use_container_width=True)

# Only trigger on button click — avoids infinite loop on rerun
if send and user_input.strip():
    query = user_input.strip()
    st.session_state["messages"].append({"role": "user", "content": query})
    st.session_state["pending_query"] = query
    # Change key to clear the input field on next render
    count = int(input_key.split("_")[-1]) + 1
    st.session_state["input_key"] = f"user_input_{count}"
    st.rerun()

if "pending_query" in st.session_state:
    query = st.session_state.pop("pending_query")
    with st.spinner("🧠 Thinking..."):
        try:
            result = agent.ask(query)
            st.session_state["messages"].append({
                "role":    "assistant",
                "content": result["answer"],
                "sources": result.get("doc_sources", []),
                "sql":     result.get("sql_query"),
            })
        except Exception as e:
            st.session_state["messages"].append({
                "role": "assistant", "content": f"⚠️ Error: {str(e)}", "sources": [], "sql": None,
            })
    st.rerun()
