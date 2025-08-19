from __future__ import annotations

import os
from datetime import date, timedelta
from typing import List

from dotenv import load_dotenv
from rich import print

from app.oura_client import OuraClient
from app.vectorstore import Chunker, VectorStore

load_dotenv()

DEFAULT_DAYS = 120

class Indexer:
    def __init__(self) -> None:
        self.vectorstore = VectorStore(persist_dir="vectorstore")
        self.chunker = Chunker()

    def sync(self, days: int = DEFAULT_DAYS) -> None:
        token = os.getenv("OURA_PERSONAL_ACCESS_TOKEN")
        if not token:
            raise RuntimeError("Set OURA_PERSONAL_ACCESS_TOKEN in your environment/.env")
        client = OuraClient(token)
        end = date.today()
        start = end - timedelta(days=days)

        sleep = client.fetch_sleep(start, end)
        readiness = client.fetch_readiness(start, end)
        activity = client.fetch_activity(start, end)
        client.close()

        sleep_rows = [s.model_dump() for s in sleep]
        readiness_rows = [r.model_dump() for r in readiness]
        activity_rows = [a.model_dump() for a in activity]

        chunks = []
        chunks += self.chunker.from_rows(sleep_rows, kind="sleep")
        chunks += self.chunker.from_rows(readiness_rows, kind="readiness")
        chunks += self.chunker.from_rows(activity_rows, kind="activity")
        self.vectorstore.add(chunks)
        print(f"Indexed {len(chunks)} chunks from {len(sleep_rows)} sleep, {len(readiness_rows)} readiness, {len(activity_rows)} activity rows.")

    def sync_data(self, days: int = DEFAULT_DAYS) -> None:
        """Alias for sync method to match Streamlit app expectations"""
        return self.sync(days)
    
    def clear_and_sync(self, days: int = DEFAULT_DAYS) -> None:
        """Clear existing data and perform a fresh sync"""
        print("🧹 Clearing existing vector store...")
        self.vectorstore.clear_store()
        print("✅ Vector store cleared")
        return self.sync(days)

if __name__ == "__main__":
    Indexer().sync()

