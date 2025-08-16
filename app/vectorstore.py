from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List
from dotenv import load_dotenv

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()

@dataclass
class DocumentChunk:
    id: str
    content: str
    metadata: Dict[str, Any]

class VectorStore:
    def __init__(self, persist_dir: str = "vectorstore") -> None:
        self.persist_dir = persist_dir
        self._embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self._store = Chroma(
            collection_name="oura_rag",
            embedding_function=self._embeddings,
            persist_directory=persist_dir,
        )

    def add(self, chunks: List[DocumentChunk]) -> None:
        if not chunks:
            return
        ids = [c.id for c in chunks]
        # Best-effort delete to support idempotent re-syncs
        try:
            self._store.delete(ids=ids)  # type: ignore[arg-type]
        except Exception:
            pass
        self._store.add_texts(
            texts=[c.content for c in chunks],
            metadatas=[c.metadata for c in chunks],
            ids=ids,
        )
        self._store.persist()

    def query(self, question: str, k: int = 6) -> List[dict]:
        results = self._store.similarity_search_with_relevance_scores(question, k=k)
        payload: List[dict] = []
        for doc, score in results:
            payload.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score),
            })
        return payload

class Chunker:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 80) -> None:
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

    def from_rows(self, rows: List[dict], kind: str) -> List[DocumentChunk]:
        chunks: List[DocumentChunk] = []
        for row in rows:
            day = row.get("day")
            content = f"Type: {kind}\nDay: {day}\nData: {row}\n"
            parts = self.splitter.split_text(content)
            for idx, part in enumerate(parts):
                chunks.append(
                    DocumentChunk(
                        id=f"{kind}-{day}-{idx}",
                        content=part,
                        metadata={"kind": kind, "day": str(day)},
                    )
                )
        return chunks