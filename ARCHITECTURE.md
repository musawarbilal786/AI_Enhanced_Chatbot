# Architecture

```mermaid
flowchart LR
    U[Student question] --> P[Privacy guard]
    P --> I[OpenAI Query / Intent Agent]
    I -->|policy or support| R[FAISS Retrieval Agent]
    I -->|greeting or personal-case refusal| A[OpenAI Answer Agent]
    R --> A
    A --> C[OpenAI Critic Agent]
    C -->|material issue| V[OpenAI Revision Agent]
    V --> C
    C -->|approved or revision limit| F[Finalizer]
    F --> UI[Streamlit UI]

    D[(Approved university PDFs)] --> E[OpenAI Embeddings]
    E --> X[(Persistent FAISS index)]
    X --> R
    UI --> FB[(Anonymous rating metrics)]
```

## Shared LangGraph state

The state carries the question, recent browser-session chat history, classified intent, retrieved FAISS chunks, grounded context, draft, critique, revision count, final answer, and page-level citation metadata. Conditional edges skip retrieval for greetings and privacy/personal-case refusals and control the critic/revision loop.

## Technology decision

The original proposal named Llama 3 as a possible open model. This implementation deliberately uses OpenAI models as the query, answer, critic and revision agents. FAISS is the persistent vector database, while OpenAI's embedding model creates document and query vectors.
