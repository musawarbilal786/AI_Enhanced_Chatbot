from src.agents.common import structured_call
from src.schemas import AgentState, CritiqueResult

SYSTEM = """You are a strict groundedness and safety reviewer.
Check whether every substantive policy claim in the draft is supported by the supplied context.
Check that citations refer to available source numbers, uncertainty is explicit, and no official personal decision is made.
Request revision only for a material issue."""


def critic_agent(state: AgentState) -> dict:
    if not state.get("context"):
        result = CritiqueResult(grounded=True, complete=True, safe=True, needs_revision=False)
    else:
        user = f"CONTEXT:\n{state['context']}\n\nDRAFT:\n{state['draft_answer']}"
        result = structured_call(SYSTEM, user, CritiqueResult)
    return {"critique": result.model_dump()}
