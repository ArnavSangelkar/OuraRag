#!/usr/bin/env python3
"""
Supabase MCP (Model Context Protocol) for Oura RAG System
This allows AI models to interact with your Supabase database
"""

import json
import os
from typing import Any, Dict, List, Optional
from datetime import date, datetime
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseMCP:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Use service role for MCP
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        
        self.supabase: Client = create_client(url, key)
    
    def get_health_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get health summary for a user"""
        try:
            end_date = date.today()
            start_date = end_date.replace(day=end_date.day - days)
            
            # Get all health data
            response = self.supabase.table("health_data").select("*").eq(
                "user_id", user_id
            ).gte("day", start_date.isoformat()).lte("day", end_date.isoformat()).execute()
            
            data = response.data
            
            # Calculate summaries
            sleep_data = [d for d in data if d["data_type"] == "sleep"]
            readiness_data = [d for d in data if d["data_type"] == "readiness"]
            activity_data = [d for d in data if d["data_type"] == "activity"]
            
            summary = {
                "user_id": user_id,
                "period_days": days,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "sleep_records": len(sleep_data),
                "readiness_records": len(readiness_data),
                "activity_records": len(activity_data),
                "total_records": len(data)
            }
            
            # Calculate averages if data exists
            if sleep_data:
                sleep_durations = [d["data"].get("total_sleep_duration", 0) for d in sleep_data]
                summary["avg_sleep_duration"] = sum(sleep_durations) / len(sleep_durations)
                summary["avg_sleep_efficiency"] = sum([d["data"].get("efficiency", 0) for d in sleep_data]) / len(sleep_data)
            
            if readiness_data:
                readiness_scores = [d["data"].get("score", 0) for d in readiness_data]
                summary["avg_readiness_score"] = sum(readiness_scores) / len(readiness_scores)
            
            if activity_data:
                steps = [d["data"].get("steps", 0) for d in activity_data]
                summary["avg_steps"] = sum(steps) / len(steps)
                summary["total_steps"] = sum(steps)
            
            return summary
            
        except Exception as e:
            return {"error": str(e)}
    
    def search_health_patterns(self, user_id: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for health patterns using vector similarity"""
        try:
            # This would require OpenAI embeddings to be generated
            # For now, return recent data
            response = self.supabase.table("health_data").select("*").eq(
                "user_id", user_id
            ).order("day", desc=True).limit(limit).execute()
            
            return response.data
            
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Generate insights for a user"""
        try:
            # Get recent data
            end_date = date.today()
            start_date = end_date.replace(day=end_date.day - 7)
            
            response = self.supabase.table("health_data").select("*").eq(
                "user_id", user_id
            ).gte("day", start_date.isoformat()).lte("day", end_date.isoformat()).execute()
            
            data = response.data
            
            insights = {
                "user_id": user_id,
                "period": "last_7_days",
                "insights": []
            }
            
            # Analyze sleep patterns
            sleep_data = [d for d in data if d["data_type"] == "sleep"]
            if sleep_data:
                sleep_durations = [d["data"].get("total_sleep_duration", 0) for d in sleep_data]
                avg_sleep = sum(sleep_durations) / len(sleep_durations)
                
                if avg_sleep < 7 * 60:  # Less than 7 hours
                    insights["insights"].append({
                        "type": "sleep",
                        "message": f"Average sleep duration is {avg_sleep/60:.1f} hours, consider getting more sleep",
                        "severity": "warning"
                    })
                elif avg_sleep > 9 * 60:  # More than 9 hours
                    insights["insights"].append({
                        "type": "sleep",
                        "message": f"Average sleep duration is {avg_sleep/60:.1f} hours, this might be excessive",
                        "severity": "info"
                    })
            
            # Analyze activity patterns
            activity_data = [d for d in data if d["data_type"] == "activity"]
            if activity_data:
                steps = [d["data"].get("steps", 0) for d in activity_data]
                avg_steps = sum(steps) / len(steps)
                
                if avg_steps < 5000:
                    insights["insights"].append({
                        "type": "activity",
                        "message": f"Average daily steps is {avg_steps:.0f}, consider increasing activity",
                        "severity": "warning"
                    })
                elif avg_steps > 12000:
                    insights["insights"].append({
                        "type": "activity",
                        "message": f"Great activity level with {avg_steps:.0f} average steps!",
                        "severity": "positive"
                    })
            
            return insights
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_data_quality_report(self, user_id: str) -> Dict[str, Any]:
        """Generate data quality report"""
        try:
            # Get all user data
            response = self.supabase.table("health_data").select("*").eq("user_id", user_id).execute()
            data = response.data
            
            report = {
                "user_id": user_id,
                "total_records": len(data),
                "data_types": {},
                "data_quality": {}
            }
            
            # Count by data type
            for record in data:
                data_type = record["data_type"]
                if data_type not in report["data_types"]:
                    report["data_types"][data_type] = 0
                report["data_types"][data_type] += 1
            
            # Check data quality
            if data:
                dates = [datetime.fromisoformat(record["day"]).date() for record in data]
                date_range = max(dates) - min(dates)
                report["data_quality"]["date_range_days"] = date_range.days
                report["data_quality"]["data_frequency"] = len(data) / max(1, date_range.days)
            
            return report
            
        except Exception as e:
            return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    mcp = SupabaseMCP()
    
    # Example: Get health summary for a user
    # summary = mcp.get_health_summary("user-uuid-here")
    # print(json.dumps(summary, indent=2))
    
    # Example: Get insights
    # insights = mcp.get_user_insights("user-uuid-here")
    # print(json.dumps(insights, indent=2))


