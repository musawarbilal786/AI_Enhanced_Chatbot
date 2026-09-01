from src.schemas import AgentState


def finalizer_agent(state: AgentState) -> dict:
    citations = []
    for i, item in enumerate(state.get("retrieved", []), 1):
        citations.append({
            "number": str(i),
            "title": item["title"],
            "url": item.get("url", ""),
            "filename": item.get("filename", ""),
            "page": item.get("page"),
            "source_type": item.get("source_type", ""),
        })
    return {"final_answer": state.get("draft_answer", ""), "citations": citations}
