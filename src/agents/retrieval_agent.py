from src.config import get_settings
from src.rag.index import VectorIndex
from src.schemas import AgentState


def retrieval_agent(state: AgentState) -> dict:
    intent = state.get("intent", {})
    if not intent.get("needs_retrieval", True):
        return {"retrieved": [], "context": ""}
    results = VectorIndex().search(intent.get("normalized_query", state["question"]))
    filtered = [r for r in results if r.score >= get_settings().min_relevance_score]
    context = "\n\n".join(
        f"[SOURCE {i}] {r.title}\nURL: {r.url}\nCATEGORY: {r.category}\nPASSAGE: {r.text}"
        for i, r in enumerate(filtered, 1)
    )
    return {"retrieved": [r.model_dump() for r in filtered], "context": context}
