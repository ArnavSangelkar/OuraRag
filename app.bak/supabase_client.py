from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
from datetime import date
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseClient:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")
        
        self.supabase: Client = create_client(url, key)
    
    def get_user_id(self) -> Optional[str]:
        """Get current user ID from Supabase auth"""
        try:
            user = self.supabase.auth.get_user()
            return user.user.id if user.user else None
        except Exception:
            return None
    
    def store_health_data(self, data_type: str, day: date, data: Dict[str, Any]) -> bool:
        """Store health data in Supabase"""
        try:
            user_id = self.get_user_id()
            if not user_id:
                return False
            
            self.supabase.table("health_data").insert({
                "user_id": user_id,
                "data_type": data_type,
                "day": day.isoformat(),
                "data": data
            }).execute()
            return True
        except Exception as e:
            print(f"Error storing health data: {e}")
            return False
    
    def get_health_data(self, data_type: str, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get health data from Supabase"""
        try:
            user_id = self.get_user_id()
            if not user_id:
                return []
            
            response = self.supabase.table("health_data").select("*").eq(
                "user_id", user_id
            ).eq("data_type", data_type).gte(
                "day", start_date.isoformat()
            ).lte("day", end_date.isoformat()).execute()
            
            return response.data
        except Exception as e:
            print(f"Error getting health data: {e}")
            return []
    
    def store_vector_chunk(self, chunk_id: str, content: str, metadata: Dict[str, Any], embedding: List[float]) -> bool:
        """Store vector chunk in Supabase"""
        try:
            user_id = self.get_user_id()
            if not user_id:
                return False
            
            self.supabase.table("vector_chunks").insert({
                "id": chunk_id,
                "user_id": user_id,
                "content": content,
                "metadata": metadata,
                "embedding": embedding
            }).execute()
            return True
        except Exception as e:
            print(f"Error storing vector chunk: {e}")
            return False
    
    def search_vector_chunks(self, query_embedding: List[float], k: int = 6) -> List[Dict[str, Any]]:
        """Search vector chunks using similarity"""
        try:
            user_id = self.get_user_id()
            if not user_id:
                return []
            
            # Use pgvector similarity search
            response = self.supabase.rpc(
                "match_vector_chunks",
                {
                    "query_embedding": query_embedding,
                    "match_count": k,
                    "user_id": user_id
                }
            ).execute()
            
            return response.data
        except Exception as e:
            print(f"Error searching vector chunks: {e}")
            return []
    
    def store_user_settings(self, oura_token: str, openai_key: str, sync_days: int = 30) -> bool:
        """Store user settings"""
        try:
            user_id = self.get_user_id()
            if not user_id:
                return False
            
            self.supabase.table("user_settings").upsert({
                "user_id": user_id,
                "oura_token": oura_token,
                "openai_key": openai_key,
                "sync_days": sync_days
            }).execute()
            return True
        except Exception as e:
            print(f"Error storing user settings: {e}")
            return False
    
    def get_user_settings(self) -> Optional[Dict[str, Any]]:
        """Get user settings"""
        try:
            user_id = self.get_user_id()
            if not user_id:
                return None
            
            response = self.supabase.table("user_settings").select("*").eq("user_id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting user settings: {e}")
            return None


