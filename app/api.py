from __future__ import annotations

import os
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI

from app.vectorstore import VectorStore

load_dotenv()

app = FastAPI(title="Oura RAG API")
vs = VectorStore(persist_dir="vectorstore")
llm = ChatOpenAI(model="gpt-4o-mini")

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    context: list

@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest) -> AskResponse:
    context_docs = vs.query(req.question, k=6)
    context_text = "\n\n".join([
        f"[Day: {d['metadata'].get('day')} Kind: {d['metadata'].get('kind')}]\n{d['content']}"
        for d in context_docs
    ])
    prompt = (
        f"""
You are a helpful assistant answering questions about the user's Oura Ring data.
Use the provided context. If uncertain, say you don't know.

Question: {req.question}

Context:
{context_text}
"""
    )
    completion = await llm.ainvoke(prompt)
    return AskResponse(answer=completion.content, context=context_docs)

