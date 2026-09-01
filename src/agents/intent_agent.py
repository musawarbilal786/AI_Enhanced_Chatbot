from src.agents.common import structured_call
from src.schemas import AgentState, IntentResult
from src.utils.privacy import find_sensitive_data

SYSTEM = """You are the query-analysis agent for a university regulations assistant.
Classify the request, rewrite it as a concise search query, and identify topics.
Mark personal case decisions, requests to evade rules, or sensitive individual data as unsafe_or_personal.
Greetings do not need retrieval. All policy/support questions do."""


def intent_agent(state: AgentState) -> dict:
    sensitive = find_sensitive_data(state["question"])
    if sensitive:
        return {
            "intent": IntentResult(
                intent="unsafe_or_personal",
                normalized_query="",
                topics=sensitive,
                needs_retrieval=False,
            ).model_dump()
        }
    result = structured_call(SYSTEM, state["question"], IntentResult)
    return {"intent": result.model_dump()}
