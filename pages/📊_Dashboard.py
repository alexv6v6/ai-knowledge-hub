"""
pages/📊_Dashboard.py
Evaluation dashboard — Streamlit multipage app (native routing).
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

st.set_page_config(
    page_title="Dashboard — AI Knowledge Hub",
    page_icon="📊",
    layout="wide",
)

from src.dashboard.stats_service import get_stats, get_all_queries, clear_log

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #f8f6f1; color: #1a1a1a; }
.dash-title {
    font-family: 'DM Mono', monospace;
    font-size: 24px; font-weight: 500;
    letter-spacing: -1px;
    border-bottom: 2px solid #1a1a1a;
    padding-bottom: 10px; margin-bottom: 4px;
}
.dash-sub { font-size: 12px; color: #888; font-family: 'DM Mono', monospace; margin-bottom: 28px; }
.metric-card { background: white; border: 1px solid #e5e0d8; border-radius: 8px; padding: 20px; text-align: center; }
.metric-val { font-family: 'DM Mono', monospace; font-size: 32px; font-weight: 500; color: #1a1a1a; }
.metric-label { font-size: 11px; color: #888; font-family: 'DM Mono', monospace; margin-top: 4px; text-transform: uppercase; letter-spacing: 1px; }
.query-card { background: white; border: 1px solid #e5e0d8; border-left: 3px solid #c8a96e; border-radius: 4px 8px 8px 4px; padding: 14px 18px; margin: 8px 0; }
.query-card.weak { border-left-color: #e07060; }
.query-q { font-size: 13px; font-weight: 500; color: #1a1a1a; margin-bottom: 6px; }
.query-meta { font-family: 'DM Mono', monospace; font-size: 10px; color: #888; }
.score-pill { display: inline-block; padding: 2px 10px; border-radius: 20px; font-family: 'DM Mono', monospace; font-size: 11px; font-weight: 500; }
.score-good { background: #e8f4e8; color: #2d6a2d; border: 1px solid #b8d4b8; }
.score-ok   { background: #fff8e8; color: #8b6914; border: 1px solid #e8d496; }
.score-bad  { background: #fde8e8; color: #8b2020; border: 1px solid #e8b4b4; }
.section-title { font-family: 'DM Mono', monospace; font-size: 13px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; margin: 24px 0 12px 0; padding-bottom: 6px; border-bottom: 1px solid #e5e0d8; }
.stButton > button { background: #1a1a1a !important; color: #f8f6f1 !important; border: none !important; border-radius: 6px !important; font-family: 'DM Mono', monospace !important; font-size: 11px !important; }
</style>
""", unsafe_allow_html=True)


def score_class(s): return "score-good" if s >= 4.0 else ("score-ok" if s >= 3.0 else "score-bad")
def score_emoji(s): return "🟢" if s >= 4.5 else ("🟡" if s >= 4.0 else ("🟠" if s >= 3.0 else "🔴"))


st.markdown('<div class="dash-title">📊 Evaluation Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="dash-sub">Query history · Score trends · Metric breakdown</div>', unsafe_allow_html=True)

stats = get_stats()
all_q = get_all_queries()

if stats["total_queries"] == 0:
    st.markdown("""
    <div style="text-align:center; padding:80px 20px;">
        <div style="font-size:48px; margin-bottom:16px;">📭</div>
        <div style="font-family:'DM Mono',monospace; font-size:14px; color:#666;">No queries evaluated yet</div>
        <div style="font-size:12px; margin-top:8px; color:#999;">Go to Chat and ask some questions</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# KPIs
st.markdown('<div class="section-title">Overview</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
for col, val, label, color in [
    (c1, stats['total_queries'], "Total Queries", "#1a1a1a"),
    (c2, stats['avg_score'],     "Avg Score /5.0", "#1a1a1a"),
    (c3, stats['best_score'],    "Best Score",    "#2d6a2d"),
    (c4, stats['worst_score'],   "Worst Score",   "#e07060"),
]:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val" style="color:{color}">{val}</div>
            <div class="metric-label">{label}</div>
        </div>""", unsafe_allow_html=True)

# Metric breakdown
if stats["by_metric"]:
    st.markdown('<div class="section-title">Metric Breakdown</div>', unsafe_allow_html=True)
    metrics = [("relevance","Relevance"),("completeness","Completeness"),("conciseness","Conciseness"),("accuracy","Accuracy"),("language_match","Language")]
    cols = st.columns(5)
    for col, (m, label) in zip(cols, metrics):
        val = stats["by_metric"].get(m, 0.0)
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val" style="font-size:24px">{val}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

# Score over time
if len(all_q) >= 2:
    st.markdown('<div class="section-title">Score Over Time</div>', unsafe_allow_html=True)
    import pandas as pd
    df = pd.DataFrame([{"Query #": e["id"], "Score": e["overall"]} for e in all_q])
    st.line_chart(df.set_index("Query #")["Score"], use_container_width=True)

# Query type distribution
if stats["by_type"]:
    st.markdown('<div class="section-title">Query Types</div>', unsafe_allow_html=True)
    cols = st.columns(max(len(stats["by_type"]), 1))
    for col, (qtype, count) in zip(cols, stats["by_type"].items()):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val" style="font-size:22px">{count}</div>
                <div class="metric-label">{qtype}</div>
            </div>""", unsafe_allow_html=True)

# Recent queries
st.markdown('<div class="section-title">Recent Queries</div>', unsafe_allow_html=True)
for entry in all_q[-10:][::-1]:
    score = entry["overall"]
    css   = "query-card weak" if score < 3.5 else "query-card"
    ts    = entry["timestamp"][:16].replace("T", " ")
    st.markdown(f"""
    <div class="{css}">
        <div class="query-q">{entry['question']}</div>
        <div class="query-meta">
            <span class="score-pill {score_class(score)}">{score_emoji(score)} {score:.1f}/5.0</span>
            &nbsp; {ts} &nbsp;·&nbsp; {entry.get('query_type','—')}
            {" &nbsp;·&nbsp; SQL" if entry.get('sql_query') else ""}
        </div>
        {"<div style='font-size:11px;color:#c0392b;margin-top:6px;'>⚠️ " + entry['weaknesses'] + "</div>" if score < 3.5 else ""}
    </div>""", unsafe_allow_html=True)

# Weakest queries
weak = sorted([e for e in all_q if e["overall"] < 4.0], key=lambda e: e["overall"])
if weak:
    st.markdown('<div class="section-title">⚠️ Needs Improvement (score < 4.0)</div>', unsafe_allow_html=True)
    for entry in weak[:5]:
        st.markdown(f"""
        <div class="query-card weak">
            <div class="query-q">{entry['question']}</div>
            <div class="query-meta"><span class="score-pill {score_class(entry['overall'])}">{entry['overall']:.1f}/5.0</span></div>
            <div style="font-size:12px;color:#888;margin-top:8px;">
                <b>Weakness:</b> {entry['weaknesses']}<br>
                <b>Strength:</b> {entry['strengths']}
            </div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")
if st.button("🗑 Clear evaluation history"):
    clear_log()
    st.success("History cleared")
    st.rerun()
