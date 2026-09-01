from typing import Literal
from langgraph.graph import END, START, StateGraph
from src.agents.answer_agent import answer_agent
from src.agents.critic_agent import critic_agent
from src.agents.finalizer_agent import finalizer_agent
from src.agents.intent_agent import intent_agent
from src.agents.retrieval_agent import retrieval_agent
from src.agents.revision_agent import revision_agent
from src.config import get_settings
from src.schemas import AgentState


def after_intent(state: AgentState) -> Literal["retrieve", "answer"]:
    return "retrieve" if state.get("intent", {}).get("needs_retrieval", True) else "answer"


def after_critic(state: AgentState) -> Literal["revise", "finalize"]:
    needs_revision = state.get("critique", {}).get("needs_revision", False)
    under_limit = state.get("revision_count", 0) < get_settings().max_revisions
    return "revise" if needs_revision and under_limit else "finalize"


def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("intent", intent_agent)
    builder.add_node("retrieve", retrieval_agent)
    builder.add_node("answer", answer_agent)
    builder.add_node("critic", critic_agent)
    builder.add_node("revise", revision_agent)
    builder.add_node("finalize", finalizer_agent)
    builder.add_edge(START, "intent")
    builder.add_conditional_edges("intent", after_intent)
    builder.add_edge("retrieve", "answer")
    builder.add_edge("answer", "critic")
    builder.add_conditional_edges("critic", after_critic)
    builder.add_edge("revise", "critic")
    builder.add_edge("finalize", END)
    return builder.compile()


graph = build_graph()
