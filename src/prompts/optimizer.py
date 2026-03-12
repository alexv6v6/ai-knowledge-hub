"""
optimizer.py
Automatically improves prompts using LLM feedback.
Takes a prompt + evaluation results and generates an improved version.
"""
import os
from dotenv import load_dotenv
from src.prompts.templates import PromptTemplate, PROMPT_REGISTRY

load_dotenv()

OPTIMIZER_PROMPT = """You are an expert prompt engineer. Your task is to improve a prompt based on evaluation feedback.

## Current Prompt
{current_prompt}

## Evaluation Results
Overall Score: {overall_score}/5.0
- Relevance: {relevance}/5.0
- Completeness: {completeness}/5.0
- Conciseness: {conciseness}/5.0
- Accuracy: {accuracy}/5.0
- Language Match: {language_match}/5.0

Strengths: {strengths}
Weaknesses: {weaknesses}

## Sample Questions That Performed Poorly
{poor_examples}

## Your Task
Generate an improved version of the prompt that:
1. Addresses the identified weaknesses
2. Preserves the existing strengths
3. Keeps the same purpose and scope
4. Is clear, specific, and actionable

Return ONLY the improved prompt text, no explanation or markdown."""


class PromptOptimizer:
    def __init__(self):
        from groq import Groq
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def optimize(
        self,
        prompt: PromptTemplate,
        evaluation_result,
        poor_examples: list = None,
    ) -> PromptTemplate:
        """Generate an improved version of a prompt based on evaluation feedback."""

        poor_str = "\n".join(f"- {q}" for q in (poor_examples or ["No specific examples provided"]))

        optimizer_input = OPTIMIZER_PROMPT.format(
            current_prompt=prompt.template,
            overall_score=evaluation_result.overall,
            relevance=evaluation_result.scores.get("relevance", "N/A"),
            completeness=evaluation_result.scores.get("completeness", "N/A"),
            conciseness=evaluation_result.scores.get("conciseness", "N/A"),
            accuracy=evaluation_result.scores.get("accuracy", "N/A"),
            language_match=evaluation_result.scores.get("language_match", "N/A"),
            strengths=evaluation_result.strengths,
            weaknesses=evaluation_result.weaknesses,
            poor_examples=poor_str,
        )

        improved_template = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": optimizer_input}],
            temperature=0.3,
        ).choices[0].message.content.strip()

        # Create new version
        current_version = prompt.version
        try:
            new_version = f"{float(current_version) + 0.1:.1f}"
        except ValueError:
            new_version = f"{current_version}-optimized"

        return PromptTemplate(
            name=prompt.name,
            version=new_version,
            description=f"Auto-optimized from v{current_version} — addressed: {evaluation_result.weaknesses[:80]}",
            template=improved_template,
            tags=prompt.tags + ["optimized"],
        )

    def run_optimization_cycle(
        self,
        prompt_name: str,
        test_questions: list,
        agent_fn,
        iterations: int = 2,
    ) -> PromptTemplate:
        """
        Full optimization cycle:
        1. Test current prompt with sample questions
        2. Evaluate responses
        3. Generate improved prompt
        4. Repeat for N iterations
        Returns the best prompt found.
        """
        from src.prompts.evaluator import PromptEvaluator
        from src.prompts.templates import get_prompt

        evaluator = PromptEvaluator()
        current_prompt = get_prompt(prompt_name, "latest")
        best_prompt = current_prompt
        best_score = 0.0

        print(f"\n🔄 Starting optimization cycle for '{prompt_name}'")
        print(f"   Test questions: {len(test_questions)}")
        print(f"   Iterations: {iterations}\n")

        for iteration in range(iterations):
            print(f"--- Iteration {iteration + 1}/{iterations} ---")

            # Test with sample questions
            results = []
            poor_examples = []

            for question in test_questions:
                try:
                    response_data = agent_fn(question)
                    response = response_data.get("answer", str(response_data))
                    context = str(response_data.get("doc_sources", ""))

                    result = evaluator.evaluate(
                        question=question,
                        response=response,
                        context=context,
                        prompt_name=prompt_name,
                        prompt_version=current_prompt.version,
                    )
                    results.append(result)

                    if result.overall < 3.5:
                        poor_examples.append(question)

                    print(f"  Q: {question[:50]}... → {result.overall:.1f}/5.0")

                except Exception as e:
                    print(f"  ⚠️ Error on question: {e}")

            if not results:
                print("  No results, skipping iteration")
                continue

            avg_score = sum(r.overall for r in results) / len(results)
            print(f"  Average score: {avg_score:.2f}/5.0")

            if avg_score > best_score:
                best_score = avg_score
                best_prompt = current_prompt
                print(f"  ✅ New best: v{current_prompt.version} ({best_score:.2f}/5.0)")

            # Optimize based on worst result
            worst_result = min(results, key=lambda r: r.overall)
            current_prompt = self.optimize(current_prompt, worst_result, poor_examples)
            print(f"  🔧 Generated v{current_prompt.version}")

        print(f"\n🏆 Best prompt: v{best_prompt.version} (score: {best_score:.2f}/5.0)")
        return best_prompt
