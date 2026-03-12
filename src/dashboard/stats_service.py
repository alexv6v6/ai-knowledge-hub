"""
stats_service.py
Saves and retrieves query evaluation history to/from a local JSON log.
Called automatically after each agent response.
"""
import json
import os
from datetime import datetime
from typing import List, Dict

LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "query_log.json")


def _load_log() -> List[Dict]:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    if not os.path.exists(LOG_PATH):
        return []
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_log(log: List[Dict]):
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def log_query(
    question: str,
    answer: str,
    query_type: str,
    scores: Dict[str, float],
    strengths: str,
    weaknesses: str,
    sql_query: str = None,
    doc_sources: List[str] = None,
):
    """Save a query + evaluation result to the log."""
    log = _load_log()
    entry = {
        "id":          len(log) + 1,
        "timestamp":   datetime.now().isoformat(),
        "question":    question,
        "answer":      answer[:300],  # truncate for storage
        "query_type":  query_type,
        "sql_query":   sql_query,
        "doc_sources": doc_sources or [],
        "scores":      scores,
        "strengths":   strengths,
        "weaknesses":  weaknesses,
        "overall":     scores.get("overall", 0.0),
    }
    log.append(entry)
    _save_log(log)
    return entry


def get_all_queries() -> List[Dict]:
    return _load_log()


def get_stats() -> Dict:
    log = _load_log()
    if not log:
        return {
            "total_queries": 0,
            "avg_score": 0.0,
            "best_score": 0.0,
            "worst_score": 0.0,
            "by_type": {},
            "by_metric": {},
            "recent": [],
        }

    scores   = [e["overall"] for e in log]
    avg      = sum(scores) / len(scores)
    by_type  = {}
    by_metric = {"relevance": [], "completeness": [], "conciseness": [], "accuracy": [], "language_match": []}

    for e in log:
        t = e.get("query_type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
        for m in by_metric:
            v = e.get("scores", {}).get(m)
            if v is not None:
                by_metric[m].append(v)

    metric_avgs = {m: round(sum(v)/len(v), 2) if v else 0.0 for m, v in by_metric.items()}

    return {
        "total_queries": len(log),
        "avg_score":     round(avg, 2),
        "best_score":    round(max(scores), 2),
        "worst_score":   round(min(scores), 2),
        "by_type":       by_type,
        "by_metric":     metric_avgs,
        "recent":        log[-5:][::-1],  # last 5, newest first
    }


def clear_log():
    _save_log([])
