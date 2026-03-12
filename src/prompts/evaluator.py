"""
evaluator.py
Evaluates prompt quality using LLM-as-judge with structured scoring.
Metrics: relevance, completeness, conciseness, accuracy, language_match
"""
import json
import os
from dataclasses import dataclass
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

JUDGE_PROMPT = """You are an expert evaluator of AI responses. Score the following response on these criteria.

## Question
{question}

## Context Provided
{context}

## Response to Evaluate
{response}

## Scoring Criteria (1-5 scale)
- relevance: Does the response directly answer the question? (1=off-topic, 5=perfectly on-point)
- completeness: Are all parts of the question addressed? (1=missing most, 5=fully complete)
- conciseness: Is the response appropriately brief without losing substance? (1=very verbose, 5=perfectly concise)
- accuracy: Are the facts/numbers correct based on the context? (1=many errors, 5=fully accurate)
- language_match: Does the response language match the question language? (1=wrong language, 5=perfect match)

## Output Format
Return ONLY valid JSON, no explanation:
{{
  "relevance": <1-5>,
  "completeness": <1-5>,
  "conciseness": <1-5>,
  "accuracy": <1-5>,
  "language_match": <1-5>,
  "overall": <average of above>,
  "strengths": "<one sentence>",
  "weaknesses": "<one sentence>"
}}"""


@dataclass
class EvaluationResult:
    question: str
    response: str
    prompt_name: str
    prompt_version: str
    scores: Dict[str, float]
    strengths: str
    weaknesses: str

    @property
    def overall(self) -> float:
        return self.scores.get("overall", 0.0)

    def summary(self) -> str:
        score_str = " | ".join(f"{k}: {v:.1f}" for k, v in self.scores.items() if k != "overall")
        return (
            f"Prompt: {self.prompt_name} v{self.prompt_version}\n"
            f"Overall: {self.overall:.2f}/5.0\n"
            f"Scores: {score_str}\n"
            f"✅ {self.strengths}\n"
            f"⚠️  {self.weaknesses}"
        )


class PromptEvaluator:
    def __init__(self):
        from groq import Groq
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def evaluate(
        self,
        question: str,
        response: str,
        context: str,
        prompt_name: str,
        prompt_version: str,
    ) -> EvaluationResult:
        """Evaluate a single response using LLM-as-judge."""
        judge_input = JUDGE_PROMPT.format(
            question=question,
            context=context[:2000],  # truncate context for judge
            response=response,
        )

        raw = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": judge_input}],
            temperature=0,
        ).choices[0].message.content

        # Parse JSON response
        try:
            clean = raw.replace("```json", "").replace("```", "").strip()
            scores_data = json.loads(clean)
        except json.JSONDecodeError:
            scores_data = {
                "relevance": 0, "completeness": 0, "conciseness": 0,
                "accuracy": 0, "language_match": 0, "overall": 0,
                "strengths": "Could not parse evaluation",
                "weaknesses": "Could not parse evaluation",
            }

        scores = {
            k: float(v) for k, v in scores_data.items()
            if k not in ("strengths", "weaknesses")
        }

        return EvaluationResult(
            question=question,
            response=response,
            prompt_name=prompt_name,
            prompt_version=prompt_version,
            scores=scores,
            strengths=scores_data.get("strengths", ""),
            weaknesses=scores_data.get("weaknesses", ""),
        )

    def compare(
        self,
        question: str,
        responses: Dict[str, str],  # {"v1": response1, "v2": response2}
        context: str,
        prompt_name: str,
    ) -> List[EvaluationResult]:
        """Evaluate and compare multiple prompt versions side by side."""
        results = []
        for version, response in responses.items():
            result = self.evaluate(
                question=question,
                response=response,
                context=context,
                prompt_name=prompt_name,
                prompt_version=version,
            )
            results.append(result)

        # Sort by overall score descending
        results.sort(key=lambda r: r.overall, reverse=True)
        return results

    def print_comparison(self, results: List[EvaluationResult]):
        """Print a formatted comparison table."""
        print("\n" + "="*60)
        print("  PROMPT EVALUATION RESULTS")
        print("="*60)
        for i, r in enumerate(results):
            medal = ["🥇", "🥈", "🥉"][min(i, 2)]
            print(f"\n{medal} Rank {i+1}")
            print(r.summary())
        print("\n" + "="*60)
        winner = results[0]
        print(f"✅ Best version: {winner.prompt_name} v{winner.prompt_version} ({winner.overall:.2f}/5.0)")
        print("="*60)
