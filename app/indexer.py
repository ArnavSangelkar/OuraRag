from __future__ import annotations

import os
import uuid
from datetime import date, timedelta
from typing import List

from dotenv import load_dotenv
from rich import print

from app.oura_client import OuraClient
from app.vectorstore import Chunker, VectorStore
from app.supabase_client import SupabaseClient

load_dotenv()

DEFAULT_DAYS = 120

class Indexer:
    def __init__(self) -> None:
        self.vectorstore = VectorStore(persist_dir="vectorstore")
        self.chunker = Chunker()
        self.supabase = SupabaseClient()
        # Generate a consistent UUID for development
        self.default_user_id = str(uuid.uuid4())

    def sync(self, days: int = DEFAULT_DAYS) -> None:
        token = os.getenv("OURA_PERSONAL_ACCESS_TOKEN")
        if not token:
            raise RuntimeError("Set OURA_PERSONAL_ACCESS_TOKEN in your environment/.env")
        
        client = OuraClient(token)
        end = date.today()
        start = end - timedelta(days=days)

        print(f"🔄 Syncing Oura data from {start} to {end} ({days} days)")
        
        # Fetch data from Oura
        sleep = client.fetch_sleep(start, end)
        readiness = client.fetch_readiness(start, end)
        activity = client.fetch_activity(start, end)
        client.close()

        print(f"📊 Fetched: {len(sleep)} sleep, {len(readiness)} readiness, {len(activity)} activity records")

        # Sync to Supabase database
        print("🗄️ Syncing to Supabase database...")
        self._sync_to_supabase(sleep, readiness, activity)
        
        # Sync to vector store
        print("🔍 Syncing to vector store...")
        sleep_rows = [s.model_dump() for s in sleep]
        readiness_rows = [r.model_dump() for r in readiness]
        activity_rows = [a.model_dump() for a in activity]

        chunks = []
        chunks += self.chunker.from_rows(sleep_rows, kind="sleep")
        chunks += self.chunker.from_rows(readiness_rows, kind="readiness")
        chunks += self.chunker.from_rows(activity_rows, kind="activity")
        self.vectorstore.add(chunks)
        
        print(f"✅ Indexed {len(chunks)} chunks from {len(sleep_rows)} sleep, {len(readiness_rows)} readiness, {len(activity_rows)} activity rows.")
        print(f"✅ Data synced to both Supabase and vector store")

    def _sync_to_supabase(self, sleep_data, readiness_data, activity_data):
        """Sync data to Supabase database"""
        try:
            # Use the generated UUID for development
            default_user_id = self.default_user_id
            
            print(f"🔑 Using user ID: {default_user_id}")
            
            # Sync sleep data
            for sleep_record in sleep_data:
                # Convert the model to dict and handle date serialization
                data_dict = sleep_record.model_dump()
                # Convert date objects to ISO format strings for JSON serialization
                if 'day' in data_dict and isinstance(data_dict['day'], date):
                    data_dict['day'] = data_dict['day'].isoformat()
                
                self.supabase.store_health_data_no_auth(
                    data_type="sleep",
                    day=sleep_record.day,
                    data=data_dict,
                    user_id=default_user_id
                )
            
            # Sync readiness data
            for readiness_record in readiness_data:
                data_dict = readiness_record.model_dump()
                if 'day' in data_dict and isinstance(data_dict['day'], date):
                    data_dict['day'] = data_dict['day'].isoformat()
                
                self.supabase.store_health_data_no_auth(
                    data_type="readiness",
                    day=readiness_record.day,
                    data=data_dict,
                    user_id=default_user_id
                )
            
            # Sync activity data
            for activity_record in activity_data:
                data_dict = activity_record.model_dump()
                if 'day' in data_dict and isinstance(data_dict['day'], date):
                    data_dict['day'] = data_dict['day'].isoformat()
                
                self.supabase.store_health_data_no_auth(
                    data_type="activity",
                    day=activity_record.day,
                    data=data_dict,
                    user_id=default_user_id
                )
                
            print(f"✅ Supabase sync complete: {len(sleep_data)} sleep, {len(readiness_data)} readiness, {len(activity_data)} activity records")
            
        except Exception as e:
            print(f"❌ Error syncing to Supabase: {e}")
            print("⚠️ Data will still be available in vector store")

    def sync_data(self, days: int = DEFAULT_DAYS) -> None:
        """Alias for sync method to match Streamlit app expectations"""
        return self.sync(days)
    
    def clear_and_sync(self, days: int = DEFAULT_DAYS) -> None:
        """Clear existing data and perform a fresh sync"""
        print("🧹 Clearing existing data...")
        self.vectorstore.clear_store()
        print("✅ Vector store cleared")
        return self.sync(days)

if __name__ == "__main__":
    Indexer().sync()

