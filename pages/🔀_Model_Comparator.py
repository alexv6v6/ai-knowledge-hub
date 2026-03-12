"""
pages/🔀_Model_Comparator.py
Side-by-side LLM comparison page — ask one question, see all providers answer.
"""
import streamlit as st
import sys, os, time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

st.set_page_config(
    page_title="Model Comparator — AI Knowledge Hub",
    page_icon="🔀",
    layout="wide",
)

from src.llm.model_manager import ModelManager

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #f8f6f1; }

.page-title {
    font-family: 'DM Mono', monospace;
    font-size: 24px; font-weight: 500; letter-spacing: -1px;
    border-bottom: 2px solid #1a1a1a;
    padding-bottom: 10px; margin-bottom: 4px;
}
.page-sub { font-size: 12px; color: #888; font-family: 'DM Mono', monospace; margin-bottom: 28px; }

.provider-card {
    background: white;
    border: 1px solid #e5e0d8;
    border-radius: 10px;
    padding: 20px;
    height: 100%;
    position: relative;
}
.provider-card.winner {
    border: 2px solid #c8a96e;
    background: #fffdf7;
}
.provider-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 1px solid #f0ece4;
}
.provider-name {
    font-family: 'DM Mono', monospace;
    font-size: 13px; font-weight: 500;
    color: #1a1a1a;
}
.provider-model {
    font-family: 'DM Mono', monospace;
    font-size: 10px; color: #aaa;
}
.score-badge {
    font-family: 'DM Mono', monospace;
    font-size: 20px; font-weight: 500;
    padding: 6px 14px;
    border-radius: 8px;
}
.score-good { background: #e8f4e8; color: #2d6a2d; }
.score-ok   { background: #fff8e8; color: #8b6914; }
.score-bad  { background: #fde8e8; color: #8b2020; }
.score-none { background: #f0ece4; color: #aaa; }

.response-text {
    font-size: 13px; line-height: 1.7; color: #333;
    max-height: 320px; overflow-y: auto;
}
.metric-row {
    display: flex; gap: 8px; flex-wrap: wrap;
    margin-top: 14px; padding-top: 12px;
    border-top: 1px solid #f0ece4;
}
.metric-chip {
    font-family: 'DM Mono', monospace;
    font-size: 10px; padding: 3px 8px;
    border-radius: 20px; background: #f8f6f1;
    border: 1px solid #e5e0d8; color: #666;
}
.latency-chip {
    font-family: 'DM Mono', monospace;
    font-size: 10px; padding: 3px 8px;
    border-radius: 20px; background: #eef4ff;
    border: 1px solid #c8d8f0; color: #3a5fa0;
}
.winner-badge {
    font-family: 'DM Mono', monospace;
    font-size: 10px; padding: 2px 10px;
    border-radius: 20px;
    background: #c8a96e; color: white;
    font-weight: 500;
}
.error-box {
    background: #fde8e8; border: 1px solid #e8b4b4;
    border-radius: 6px; padding: 12px;
    font-size: 12px; color: #8b2020;
    font-family: 'DM Mono', monospace;
}
.stTextArea textarea {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    color: #1a1a1a !important;
    background: white !important;
    border: 1px solid #e5e0d8 !important;
    border-radius: 8px !important;
}
.stButton > button {
    background: #1a1a1a !important;
    color: #f8f6f1 !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'DM Mono', monospace !important;
    padding: 10px 28px !important;
    font-size: 13px !important;
}
.section-title {
    font-family: 'DM Mono', monospace;
    font-size: 12px; font-weight: 500;
    text-transform: uppercase; letter-spacing: 1px;
    color: #888; margin: 20px 0 10px 0;
}
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="page-title">🔀 Model Comparator</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Same question · Multiple models · Side-by-side evaluation</div>', unsafe_allow_html=True)

manager = ModelManager()

# ── Provider selector ──────────────────────────────────────────────────────────
PROVIDER_META = {
    "groq":   {"icon": "⚡", "color": "#F55036", "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"]},
    "ollama": {"icon": "🦙", "color": "#4a9e6b", "models": ["llama3.2", "mistral", "gemma2", "phi3", "qwen2.5"]},
    "openai": {"icon": "🤖", "color": "#10a37f", "models": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]},
    "gemini": {"icon": "✨", "color": "#4285F4", "models": ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"]},
}

st.markdown('<div class="section-title">Select providers to compare</div>', unsafe_allow_html=True)

if "selected_providers" not in st.session_state:
    st.session_state["selected_providers"] = {"groq": "llama-3.3-70b-versatile"}

cols = st.columns(4)
for col, (provider, meta) in zip(cols, PROVIDER_META.items()):
    with col:
        enabled = st.checkbox(
            f"{meta['icon']} {provider.capitalize()}",
            value=(provider in st.session_state["selected_providers"]),
            key=f"chk_{provider}",
        )
        model = st.selectbox(
            "Model",
            meta["models"],
            index=0,
            key=f"model_{provider}",
            label_visibility="collapsed",
            disabled=not enabled,
        )
        if enabled:
            st.session_state["selected_providers"][provider] = model
        else:
            st.session_state["selected_providers"].pop(provider, None)

# ── System prompt (optional) ───────────────────────────────────────────────────
with st.expander("⚙️ System prompt (optional)"):
    system_prompt = st.text_area(
        "System prompt",
        value="You are a helpful AI assistant. Answer clearly and concisely.",
        height=80,
        label_visibility="collapsed",
    )

# ── Question input ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Your question</div>', unsafe_allow_html=True)

question = st.text_area(
    "Question",
    placeholder="Ask anything — all selected models will answer simultaneously...",
    height=100,
    label_visibility="collapsed",
    key="comparator_input",
)

col_btn, col_info = st.columns([1, 4])
with col_btn:
    run = st.button("Compare →", use_container_width=True)
with col_info:
    n = len(st.session_state["selected_providers"])
    st.markdown(
        f'<div style="padding:10px 0; font-size:12px; color:#888; font-family:DM Mono,monospace;">'
        f'{n} provider{"s" if n != 1 else ""} selected · responses in parallel</div>',
        unsafe_allow_html=True
    )

# ── Run comparison ─────────────────────────────────────────────────────────────
if run and question.strip() and st.session_state["selected_providers"]:
    providers_cfg = [
        {"provider": p, "model": m}
        for p, m in st.session_state["selected_providers"].items()
    ]

    with st.spinner("⚡ Running all models in parallel..."):
        results = manager.compare(
            prompt=question.strip(),
            system=system_prompt,
            providers=providers_cfg,
        )

    # ── Evaluate each response ─────────────────────────────────────────────
    scored_results = []
    try:
        from src.prompts.evaluator import PromptEvaluator
        evaluator = PromptEvaluator()
        for r in results:
            if r.success:
                eval_result = evaluator.evaluate(
                    question=question.strip(),
                    response=r.content,
                    context="",
                    prompt_name="comparison",
                    prompt_version="v1",
                )
                scored_results.append((r, eval_result))
            else:
                scored_results.append((r, None))
    except Exception:
        scored_results = [(r, None) for r in results]

    # ── Find winner ────────────────────────────────────────────────────────
    winner_provider = None
    best_score = 0
    for r, ev in scored_results:
        if ev and r.success:
            s = ev.scores.get("overall", 0)
            if s > best_score:
                best_score    = s
                winner_provider = r.provider

    st.session_state["comparison_results"] = scored_results
    st.session_state["comparison_question"] = question.strip()
    st.session_state["comparison_winner"]   = winner_provider

# ── Display results ────────────────────────────────────────────────────────────
if "comparison_results" in st.session_state:
    results      = st.session_state["comparison_results"]
    winner       = st.session_state.get("comparison_winner")
    shown_q      = st.session_state.get("comparison_question", "")

    st.markdown(f"""
    <div style="background:white; border:1px solid #e5e0d8; border-radius:8px;
                padding:14px 18px; margin:20px 0 16px 0;">
        <div style="font-size:11px; color:#aaa; font-family:DM Mono,monospace; margin-bottom:4px;">QUESTION</div>
        <div style="font-size:14px; font-weight:500; color:#1a1a1a;">{shown_q}</div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(len(results))
    for col, (r, ev) in zip(cols, results):
        meta  = PROVIDER_META.get(r.provider, {"icon": "🤖", "color": "#888"})
        is_winner = (r.provider == winner)

        with col:
            card_class = "provider-card winner" if is_winner else "provider-card"

            score_html = ""
            metrics_html = ""
            if ev and r.success:
                s = ev.scores.get("overall", 0)
                sc = "score-good" if s >= 4.0 else ("score-ok" if s >= 3.0 else "score-bad")
                score_html = f'<span class="score-badge {sc}">{s:.1f}</span>'

                chips = "".join([
                    f'<span class="metric-chip">{k[:4]} {v:.0f}</span>'
                    for k, v in ev.scores.items() if k != "overall"
                ])
                metrics_html = f'<div class="metric-row">{chips}</div>'
            else:
                score_html = '<span class="score-badge score-none">—</span>'

            winner_html = '<span class="winner-badge">🏆 winner</span>' if is_winner else ""

            if r.success:
                body = f'<div class="response-text">{r.content}</div>'
            else:
                body = f'<div class="error-box">⚠️ {r.error}</div>'

            st.markdown(f"""
            <div class="{card_class}">
                <div class="provider-header">
                    <div>
                        <div class="provider-name">{meta['icon']} {r.provider.capitalize()} {winner_html}</div>
                        <div class="provider-model">{r.model}</div>
                    </div>
                    {score_html}
                </div>
                {body}
                <div class="metric-row">
                    <span class="latency-chip">⏱ {r.latency_ms:.0f}ms</span>
                    {"" if not ev else ""}
                </div>
                {metrics_html}
            </div>
            """, unsafe_allow_html=True)

    # ── Summary table ──────────────────────────────────────────────────────
    if any(ev for _, ev in results):
        st.markdown('<div class="section-title" style="margin-top:32px;">Summary</div>', unsafe_allow_html=True)
        import pandas as pd
        rows = []
        for r, ev in results:
            row = {
                "Provider":  f"{PROVIDER_META.get(r.provider,{}).get('icon','🤖')} {r.provider}",
                "Model":     r.model,
                "Score":     ev.scores.get("overall", "—") if ev else "error",
                "Relevance": ev.scores.get("relevance", "—") if ev else "—",
                "Accuracy":  ev.scores.get("accuracy", "—") if ev else "—",
                "Latency":   f"{r.latency_ms:.0f}ms",
            }
            rows.append(row)
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Clear ──────────────────────────────────────────────────────────────
    if st.button("🗑 Clear results"):
        for k in ["comparison_results", "comparison_question", "comparison_winner"]:
            st.session_state.pop(k, None)
        st.rerun()
