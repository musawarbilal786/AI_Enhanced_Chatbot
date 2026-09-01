from src.agents.common import text_call
from src.schemas import AgentState

SYSTEM = """You are a student-support answer agent for Ulster University and its London branch campus.
Use only the supplied official-source context for factual policy claims.
Give a direct, readable answer. Cite claims using [1], [2], etc matching SOURCE numbers.
Never invent deadlines, eligibility decisions, contacts, or procedures.
When evidence is insufficient, say so and direct the user to the official university/QA support team.
This tool provides guidance, not an official determination."""


def answer_agent(state: AgentState) -> dict:
    intent = state.get("intent", {})
    if intent.get("intent") == "greeting":
        return {"draft_answer": "Hello! Ask me about Ulster University regulations, assessment rules, appeals, attendance, student conduct, support, or London branch-campus policies."}
    if intent.get("intent") == "unsafe_or_personal":
        return {"draft_answer": "I can explain published regulations, but I cannot make an official decision about an individual case or help bypass university rules. Please contact the relevant university or QA Higher Education support team for case-specific advice."}
    if not state.get("context"):
        return {"draft_answer": "I could not find sufficiently relevant evidence in the indexed official documents. Please check the official Ulster University or QA Higher Education policy pages, or contact student support for confirmation."}
    history = "\n".join(f'{m.get("role")}: {m.get("content")}' for m in state.get("chat_history", [])[-6:])
    prompt = f"QUESTION:\n{state['question']}\n\nRECENT CHAT:\n{history}\n\nOFFICIAL CONTEXT:\n{state['context']}"
    return {"draft_answer": text_call(SYSTEM, prompt)}
