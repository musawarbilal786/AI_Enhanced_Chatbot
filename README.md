# Ulster University Multi-Agent PDF-RAG Chatbot

A complete Streamlit research prototype built with **LangGraph**, **OpenAI agents**, **FAISS**, and retrieval-augmented generation. The knowledge base uses the three PDF files supplied with this project, not a manually written summary dataset. OpenAI models are intentionally used as the agents instead of Llama 3, while FAISS provides the required persistent vector database.

## Included dataset

The files are bundled in `data/pdfs/`:

- `prospectus_post_graduate.pdf` - Ulster University International Postgraduate Prospectus 2025/26
- `prospectus_under_graduate.pdf` - Ulster University Undergraduate Prospectus 2025/26
- `rules_and_regulations.pdf` - University of Ulster Regulations

`data/pdf_manifest.json` stores document titles and categories. During ingestion, each PDF is read page-by-page, split into overlapping chunks, embedded with OpenAI, and stored with its filename and page number. Answers therefore cite sources such as **University of Ulster Regulations, page 13**.

## Multi-agent workflow

1. **Intent agent** identifies the question type and creates a retrieval query.
2. **Retrieval agent** searches the PDF vector index.
3. **Answer agent** writes a response grounded only in retrieved passages.
4. **Critic agent** checks factual grounding, completeness, safety, and citations.
5. **Revision agent** repairs an answer when the critic finds problems.
6. **Finalizer agent** returns the answer and page-level source metadata to Streamlit.

LangGraph controls shared state, conditional routing, and the critic/revision loop.

## Project structure

```text
ulster_multiagent_chatbot/
├── app/streamlit_app.py
├── data/
│   ├── pdfs/                         # Three supplied PDF dataset files
│   ├── pdf_manifest.json             # PDF metadata
│   └── processed/                    # Generated vector index
├── scripts/
│   ├── inspect_pdfs.py               # Page count, size and SHA-256 inventory
│   ├── build_index.py                # Extract, chunk and embed PDFs
│   └── evaluate.py                   # Evaluation questions
├── src/
│   ├── agents/                       # Separate LangGraph agent nodes
│   ├── rag/pdf_loader.py             # Page-level PDF extraction
│   ├── rag/index.py                  # Persistent NumPy vector search
│   ├── graph.py                      # LangGraph workflow
│   └── config.py
└── tests/
```

## Installation

Python 3.11 or 3.12 is recommended.

```bash
python -m venv .venv
```

Activate the environment:

```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

Install packages and create the environment file:

```bash
pip install -r requirements.txt
cp .env.example .env
```

On Windows, use `copy .env.example .env`.

Set your OpenAI key in `.env`:

```env
OPENAI_API_KEY=sk-your-key
OPENAI_CHAT_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
USE_MANUAL_DATASET=false
```

## Verify and index the supplied PDFs

```bash
python scripts/inspect_pdfs.py
python scripts/build_index.py
```

The index builder creates a persistent FAISS index under `data/faiss_index/`. The generated database is not bundled because it depends on your OpenAI embedding model and API key.

## Run the Streamlit UI

```bash
streamlit run app/streamlit_app.py
```

Example questions:

- What counts as academic misconduct involving generative AI?
- What evidence is required for extenuating circumstances?
- What postgraduate programmes are listed for computing?
- What support and facilities are described for undergraduate students?
- Can a student bring a smartwatch into an examination?

## Tests

```bash
pytest -q
```

## Important limitations

- The chatbot is a guidance and document-discovery prototype, not an official University decision-maker.
- Prospectus information applies to the stated 2025/26 cycle and may later change.
- The rules PDF should be checked for its effective/version date before relying on it operationally.
- Users should verify high-impact matters with the University and the cited PDF page.
- Do not submit names, student numbers, medical records, immigration documents, or disciplinary case files through the prototype.


## Research-objective features

- Natural-language query and intent analysis through an OpenAI agent.
- Persistent FAISS semantic retrieval over approved PDF documents.
- Page-level evidence and source-grounded answers.
- Browser-session conversational context and follow-up support.
- OpenAI answer, critic and revision agents controlled by LangGraph.
- Personal-data screening, guidance-only limitations and safe refusal behaviour.
- Automatic latency/source metrics, anonymous helpfulness ratings, and an evaluation worksheet with independent human-scoring fields.
- Automatic first-run indexing and a manual **Re-embed PDFs** control.
