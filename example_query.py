"""
example_query.py
Quick demo of the AI Knowledge Hub — no setup required beyond .env
"""
from src.agents.knowledge_agent import KnowledgeAgent

agent = KnowledgeAgent()

print("\n" + "="*50)
print("  AI Knowledge Hub — Example Queries")
print("="*50)

# ── Document query (RAG) ───────────────────────────────
print("\n[1] Document query (RAG)")
response = agent.ask("What is a RAG system?")
print("Q: What is a RAG system?")
print("A:", response["answer"])

# ── Database query (Text-to-SQL) ───────────────────────
print("\n[2] Database query (Text-to-SQL)")
response = agent.ask("What products do we have in stock?")
print("Q: What products do we have in stock?")
print("A:", response["answer"])
if response["sql_query"]:
    print("SQL:", response["sql_query"])

# ── Combined query ─────────────────────────────────────
print("\n[3] Combined query")
response = agent.ask("Show me the top selling products")
print("Q: Show me the top selling products")
print("A:", response["answer"])

print("\n" + "="*50)
print("  Status:", agent.status())
print("="*50)
