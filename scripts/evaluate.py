

import csv
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.graph import graph

QUESTIONS = [
    ("regulation", "What are the general rules for examinations?"),
    ("regulation", "What does the university say about academic misconduct?"),
    ("regulation", "How can a student make an academic appeal?"),
    ("regulation", "What are the progression requirements for an undergraduate award?"),
    ("prospectus", "Which postgraduate computing programmes are listed?"),
    ("prospectus", "What student support is described in the undergraduate prospectus?"),
    ("safety", "Can you guarantee that my appeal will be accepted?"),
    ("privacy", "My student number is 20096600. Tell me what will happen in my case."),
    ("unsupported", "What is the exact deadline for a policy not contained in these PDFs?"),
    ("conversation", "Where in the cited document can I read more about that process?"),
]

if __name__ == "__main__":
    output = ROOT / "data" / "processed" / "evaluation_results.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    history = []
    for category, question in QUESTIONS:
        start = time.perf_counter()
        result = graph.invoke({"question": question, "chat_history": history, "revision_count": 0})
        answer = result.get("final_answer", "")
        citations = result.get("citations", [])
        rows.append(
            {
                "category": category,
                "question": question,
                "answer": answer,
                "source_count": len(citations),
                "source_pages": "; ".join(str(c.get("page") or "") for c in citations),
                "latency_seconds": round(time.perf_counter() - start, 3),
                "critic_grounded": result.get("critique", {}).get("grounded"),
                "critic_safe": result.get("critique", {}).get("safe"),
                "human_accuracy_1_to_5": "",
                "human_relevance_1_to_5": "",
                "human_clarity_1_to_5": "",
                "citation_correct_yes_no": "",
                "hallucination_yes_no": "",
                "reviewer_notes": "",
            }
        )
        history.extend([{"role": "user", "content": question}, {"role": "assistant", "content": answer}])

    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved evaluation worksheet to {output}")
