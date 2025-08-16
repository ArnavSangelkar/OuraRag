## Oura RAG

Answer questions about your Oura Ring data using a Retrieval-Augmented Generation (RAG) pipeline.

### Setup

1) Create and activate venv (already created by scaffolding):

```bash
cd ~/oura-rag
source .venv/bin/activate
```

2) Copy env template and set your keys:

```bash
cp .env.example .env
# Edit .env and set:
# OURA_PERSONAL_ACCESS_TOKEN=...  # from https://cloud.ouraring.com/personal-access-tokens
# OPENAI_API_KEY=...              # for embeddings + chat
```

3) Initial sync (fetches last 120 days and indexes into local Chroma):

```bash
./sync.sh 120
```

4) Ask a question via CLI:

```bash
./ask.sh "How did my average HRV trend in the last month?"
```

5) Run API:

```bash
./run_api.sh
# POST to http://localhost:8000/ask with {"question": "..."}
```

### Notes
- Vector store persists under `vectorstore/`.
- You can re-run sync anytime; identical IDs prevent duplicate chunking.
- Models used: `text-embedding-3-large` for embeddings, `gpt-4o-mini` for chat. Adjust in `app/vectorstore.py` and `app/cli.py` / `app/api.py`.

