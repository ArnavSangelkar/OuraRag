from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List
from datetime import datetime
import uuid
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
        
        # Clear existing collection to avoid duplicate ID conflicts
        try:
            self._store.delete_collection()
            self._store = Chroma(
                collection_name="oura_rag",
                embedding_function=self._embeddings,
                persist_directory=self.persist_dir,
            )
        except Exception:
            pass
        
        # Add new chunks with fresh collection
        ids = [c.id for c in chunks]
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
    
    def clear_store(self) -> None:
        """Clear the entire vector store"""
        try:
            self._store.delete_collection()
            self._store = Chroma(
                collection_name="oura_rag",
                embedding_function=self._embeddings,
                persist_directory=self.persist_dir,
            )
        except Exception as e:
            print(f"Warning: Could not clear store: {e}")
    
    def get_stats(self) -> dict:
        """Get statistics about the vector store"""
        try:
            count = self._store._collection.count()
            return {"total_documents": count}
        except Exception:
            return {"total_documents": 0}

class Chunker:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 80) -> None:
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

    def from_rows(self, rows: List[dict], kind: str) -> List[DocumentChunk]:
        chunks: List[DocumentChunk] = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for row in rows:
            day = row.get("day")
            content = f"Type: {kind}\nDay: {day}\nData: {row}\n"
            parts = self.splitter.split_text(content)
            for idx, part in enumerate(parts):
                # Generate unique ID with timestamp and UUID to avoid conflicts
                unique_id = f"{kind}-{day}-{idx}-{timestamp}-{str(uuid.uuid4())[:8]}"
                chunks.append(
                    DocumentChunk(
                        id=unique_id,
                        content=part,
                        metadata={"kind": kind, "day": str(day), "timestamp": timestamp},
                    )
                )
        return chunks