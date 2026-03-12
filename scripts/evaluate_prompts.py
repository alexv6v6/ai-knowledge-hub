"""
scripts/evaluate_prompts.py
Runs a full evaluation and comparison of all prompt versions.
Usage: python scripts/evaluate_prompts.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.prompts.templates import get_prompt, list_prompts
from src.prompts.evaluator import PromptEvaluator
from src.agents.knowledge_agent import KnowledgeAgent

# ── Test questions ─────────────────────────────────────────────────────────────
TEST_QUESTIONS = [
    # English — database
    "What products are low on stock?",
    "Which customers are from Bogotá?",
    "What is the total revenue from sales?",
    # Spanish — database
    "¿Qué productos tenemos en inventario?",
    "¿Cuántos clientes tenemos en total?",
    # English — document (requires ingested docs)
    "Summarize the main topics in the documents",
    # Mixed
    "Show me the top selling products and explain why they matter",
]

def run_evaluation():
    print("🧠 AI Knowledge Hub — Prompt Evaluation")
    print("="*50)

    agent    = KnowledgeAgent()
    evaluator = PromptEvaluator()

    # Pick a few representative questions
    questions = TEST_QUESTIONS[:4]

    print(f"\nEvaluating {len(questions)} questions...\n")

    all_results = []
    for question in questions:
        print(f"Q: {question}")
        try:
            result_data = agent.ask(question)
            response    = result_data.get("answer", "")
            context     = str(result_data.get("doc_sources", "")) + str(result_data.get("sql_query", ""))

            result = evaluator.evaluate(
                question=question,
                response=response,
                context=context,
                prompt_name="knowledge_agent_system",
                prompt_version="v2",
            )
            all_results.append(result)
            print(f"   Score: {result.overall:.1f}/5.0 — {result.strengths[:60]}\n")

        except Exception as e:
            print(f"   ⚠️ Error: {e}\n")

    if all_results:
        avg = sum(r.overall for r in all_results) / len(all_results)
        print("="*50)
        print(f"📊 Average score across {len(all_results)} questions: {avg:.2f}/5.0")

        # Show worst performing
        worst = min(all_results, key=lambda r: r.overall)
        print(f"\n⚠️  Weakest question ({worst.overall:.1f}/5.0):")
        print(f"   Q: {worst.question}")
        print(f"   Weakness: {worst.weaknesses}")
        print(f"\n💡 Suggestion: Run optimizer on this prompt to improve it.")
        print(f"   from src.prompts.optimizer import PromptOptimizer")
        print(f"   optimizer = PromptOptimizer()")


def compare_prompt_versions():
    """Compare v1 vs v2 of the text_to_sql prompt."""
    print("\n🔍 Comparing text_to_sql v1 vs v2")
    print("="*50)

    v1 = get_prompt("text_to_sql", "v1")
    v2 = get_prompt("text_to_sql", "v2")

    print(f"\nv1 template length: {len(v1.template)} chars")
    print(f"v2 template length: {len(v2.template)} chars")
    print(f"\nv2 improvements: {v2.description}")
    print(f"v2 tags: {v2.tags}")


if __name__ == "__main__":
    print("\nAvailable prompts:", list_prompts())
    print()
    compare_prompt_versions()
    print()
    run_evaluation()
