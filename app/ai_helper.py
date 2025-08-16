from __future__ import annotations

from app.vectorstore import VectorStore
from langchain_openai import ChatOpenAI

def ask_ai(question: str) -> str:
    """Query the vector store and get an AI answer. Returns the answer as a string."""
    try:
        vs = VectorStore(persist_dir="vectorstore")
        docs = vs.query(question, k=6)
        
        if not docs:
            return "I don't have enough data to answer your question. Please sync some Oura data first."
        
        context = "\n\n".join([
            f"[Day: {d['metadata'].get('day')} Kind: {d['metadata'].get('kind')}]\n{d['content']}"
            for d in docs
        ])
        
        llm = ChatOpenAI(model="gpt-4o-mini")
        prompt = (
            f"""
You are a helpful assistant answering questions about the user's Oura Ring data.
Use the provided context to answer the question. If uncertain, say you don't know.
Be conversational and helpful.

Question: {question}

Context:
{context}

Answer:"""
        )
        
        completion = llm.invoke(prompt)
        return completion.content
        
    except Exception as e:
        return f"Sorry, I encountered an error while processing your question: {str(e)}"


