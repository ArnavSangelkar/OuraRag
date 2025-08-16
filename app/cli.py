from __future__ import annotations

import typer
from dotenv import load_dotenv
from rich import print

from app.indexer import Indexer
from app.vectorstore import VectorStore
from langchain_openai import ChatOpenAI

app = typer.Typer(add_completion=False)
load_dotenv()

@app.command()
def sync(days: int = typer.Option(120, help="Days of history to sync")) -> None:
    """Fetch Oura data and index into the vector store.
    Requires OURA_PERSONAL_ACCESS_TOKEN in environment or .env
    """
    Indexer().sync(days=days)

@app.command()
def ask(question: str = typer.Argument(..., help="Your question about your Oura data")) -> None:
    """Query the vector store and get an answer. Requires OPENAI_API_KEY.
    """
    vs = VectorStore(persist_dir="vectorstore")
    docs = vs.query(question, k=6)
    context = "\n\n".join([
        f"[Day: {d['metadata'].get('day')} Kind: {d['metadata'].get('kind')}]\n{d['content']}"
        for d in docs
    ])
    llm = ChatOpenAI(model="gpt-4o-mini")
    prompt = (
        f"""
You are a helpful assistant answering questions about the user's Oura Ring data.
Use the provided context. If uncertain, say you don't know.

Question: {question}

Context:
{context}
"""
    )
    completion = llm.invoke(prompt)
    print(completion.content)

if __name__ == "__main__":
    app()

