from src.agents.common import text_call
from src.schemas import AgentState

SYSTEM = """Revise the answer to resolve the review issues.
Use only the supplied context. Preserve correct [n] citations. Be concise, clear, cautious, and useful.
Do not mention the internal review process."""


def revision_agent(state: AgentState) -> dict:
    issues = "\n".join(f"- {x}" for x in state.get("critique", {}).get("issues", []))
    prompt = f"QUESTION:\n{state['question']}\n\nCONTEXT:\n{state['context']}\n\nDRAFT:\n{state['draft_answer']}\n\nISSUES:\n{issues}"
    return {
        "draft_answer": text_call(SYSTEM, prompt),
        "revision_count": state.get("revision_count", 0) + 1,
    }
