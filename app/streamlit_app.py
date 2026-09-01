import json
import sys
import time
import traceback
import warnings
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

warnings.filterwarnings(
    "ignore",
    message=r"The default value of `allowed_objects` will change in a future version.*",
    category=Warning,
    module=r"langgraph\.checkpoint\.base.*",
)

st.set_page_config(page_title="Ulster Regulations Assistant", page_icon="🎓", layout="wide")
st.title("🎓 Ulster University Regulations Assistant")
st.caption("Multi-agent PDF-RAG prototype using official prospectuses, regulations, handbooks and policy documents")


def stop_with_startup_error(exc: Exception) -> None:
    """Show import/configuration failures in the browser instead of exiting silently."""
    log_dir = ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "startup_error.log"
    log_file.write_text(traceback.format_exc(), encoding="utf-8")
    st.error("The application could not finish starting.")
    st.exception(exc)
    st.info(f"A copy of this error was written to: {log_file}")
    st.stop()


try:
    from src.config import get_settings
    from src.rag.index import VectorIndex, load_documents
except Exception as exc:
    stop_with_startup_error(exc)


@st.cache_resource(show_spinner=False)
def get_vector_index() -> "VectorIndex":
    return VectorIndex()


def get_graph():
    # Importing the graph loads LangGraph and OpenAI-related modules. Keeping it
    # lazy means FAISS or model import failures can be displayed in Streamlit.
    try:
        from src.graph import graph
        return graph
    except Exception as exc:
        stop_with_startup_error(exc)


def render_sources(sources: list[dict]) -> None:
    for source in sources:
        page = f", page {source['page']}" if source.get("page") else ""
        label = f"{source['title']}{page}"
        if source.get("url"):
            st.markdown(f"{source['number']}. [{label}]({source['url']})")
        else:
            st.markdown(f"{source['number']}. {label}")


def index_exists() -> bool:
    return get_vector_index().exists()


def save_anonymous_feedback(rating: str, latency: float, source_count: int) -> None:
    output = get_settings().index_dir / "anonymous_feedback.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "rating": rating,
        "latency_seconds": round(latency, 3),
        "source_count": source_count,
    }
    with output.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def build_embeddings() -> int:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. In the project folder, copy .env.example "
            "to .env and put your real OpenAI API key in it."
        )
    documents = load_documents()
    return get_vector_index().build(documents)


# First-run indexing remains automatic, but failures no longer kill the process.
if not index_exists():
    st.info("No FAISS knowledge base was found. Creating it for the first run…")
    try:
        with st.spinner("Reading PDFs and creating OpenAI embeddings. This may take several minutes…"):
            chunk_count = build_embeddings()
        st.success(f"Knowledge base created successfully with {chunk_count:,} text chunks.")
        st.rerun()
    except Exception as exc:
        st.error("The knowledge base could not be created. The app is still running so you can review the error below.")
        st.exception(exc)
        st.warning("After correcting the problem, use the Re-embed PDFs button in the sidebar.")

with st.sidebar:
    st.header("About")

    ready = index_exists()
    if ready:
        st.success(f"FAISS ready · {get_vector_index().count():,} chunks")
    else:
        st.error("Knowledge base missing")

    if st.button("Re-embed PDFs", use_container_width=True, help="Rebuild FAISS from all PDFs in data/pdfs."):
        try:
            with st.spinner("Rebuilding FAISS from the PDFs…"):
                chunk_count = build_embeddings()
            st.success(f"Re-embedded {chunk_count:,} text chunks.")
            st.rerun()
        except Exception as exc:
            st.error("Re-embedding failed. The application has not closed.")
            st.exception(exc)

    show_debug = st.toggle("Show agent details", value=False)
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("Official PDF sources"):
                render_sources(message["sources"])

question = st.chat_input(
    "Ask about assessments, appeals, attendance, conduct, support, fees, or regulations…",
    disabled=not index_exists(),
)
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Consulting the PDF policy agents…"):
            started = time.perf_counter()
            history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
            try:
                result = get_graph().invoke({"question": question, "chat_history": history, "revision_count": 0})
                answer = result["final_answer"]
                sources = result.get("citations", [])
                latency = time.perf_counter() - started
                st.markdown(answer)
                if sources:
                    with st.expander("Official PDF sources"):
                        render_sources(sources)
                st.caption(f"Response time: {latency:.2f} seconds · {len(sources)} source(s)")
                feedback_key = f"feedback_{len(st.session_state.messages)}"
                feedback = st.feedback("thumbs", key=feedback_key)
                if feedback is not None and not st.session_state.get(feedback_key + "_saved"):
                    save_anonymous_feedback("helpful" if feedback == 1 else "not_helpful", latency, len(sources))
                    st.session_state[feedback_key + "_saved"] = True
                    st.toast("Anonymous feedback saved. No question or answer text was recorded.")
                if show_debug:
                    with st.expander("Agent trace"):
                        st.json({
                            "intent": result.get("intent"),
                            "retrieved_scores": [round(x["score"], 3) for x in result.get("retrieved", [])],
                            "retrieved_pages": [x.get("page") for x in result.get("retrieved", [])],
                            "critique": result.get("critique"),
                            "revision_count": result.get("revision_count", 0),
                        })
            except Exception as exc:
                answer, sources = f"Configuration or runtime error: `{exc}`", []
                latency = time.perf_counter() - started
                st.error(answer)
                st.exception(exc)
    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
