#!/usr/bin/env python3
"""
Enhanced Supabase MCP (Model Context Protocol) for Oura RAG System
This allows AI models to interact with your Supabase database with comprehensive health data
"""

import json
import os
from typing import Any, Dict, List, Optional
from datetime import date, timedelta, datetime
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
        # For development, get any existing user ID from the database
        self._cached_user_id = None
    
    def _get_user_id(self, user_id: Optional[str] = None) -> str:
        """Get user ID, finding any existing user in the database if none provided"""
        if user_id:
            return user_id
        
        # Cache the user ID to avoid repeated queries
        if self._cached_user_id:
            return self._cached_user_id
            
        # Find any existing user ID from the database
        try:
            response = self.supabase.table("health_data").select("user_id").limit(1).execute()
            if response.data:
                self._cached_user_id = response.data[0]["user_id"]
                return self._cached_user_id
        except Exception:
            pass
            
        # Fallback to default UUID format
        return "default-user"
    
    def get_health_summary(self, user_id: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive health summary for a user"""
        try:
            user_id = self._get_user_id(user_id)
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
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
            
            # Enhanced sleep analysis with new fields
            if sleep_data:
                # Basic metrics
                sleep_durations = [d["data"].get("total_sleep_duration", 0) for d in sleep_data if d["data"].get("total_sleep_duration") is not None and d["data"].get("total_sleep_duration") > 0]
                if sleep_durations:
                    summary["avg_sleep_duration"] = sum(sleep_durations) / len(sleep_durations)
                    summary["avg_sleep_duration_hours"] = summary["avg_sleep_duration"] / 3600
                
                # Sleep quality metrics
                efficiencies = [d["data"].get("efficiency", 0) for d in sleep_data if d["data"].get("efficiency") is not None and d["data"].get("efficiency") > 0]
                if efficiencies:
                    summary["avg_sleep_efficiency"] = sum(efficiencies) / len(efficiencies)
                
                # Sleep stage analysis
                deep_sleep = [d["data"].get("deep_sleep_duration", 0) for d in sleep_data if d["data"].get("deep_sleep_duration") is not None and d["data"].get("deep_sleep_duration") >= 0]
                rem_sleep = [d["data"].get("rem_sleep_duration", 0) for d in sleep_data if d["data"].get("rem_sleep_duration") is not None and d["data"].get("rem_sleep_duration") >= 0]
                light_sleep = [d["data"].get("light_sleep_duration", 0) for d in sleep_data if d["data"].get("light_sleep_duration") is not None and d["data"].get("light_sleep_duration") >= 0]
                
                if deep_sleep:
                    summary["avg_deep_sleep_hours"] = sum(deep_sleep) / len(deep_sleep) / 3600
                if rem_sleep:
                    summary["avg_rem_sleep_hours"] = sum(rem_sleep) / len(rem_sleep) / 3600
                if light_sleep:
                    summary["avg_light_sleep_hours"] = sum(light_sleep) / len(light_sleep) / 3600
                
                # Sleep scores
                sleep_scores = [d["data"].get("score", 0) for d in sleep_data if d["data"].get("score") is not None and d["data"].get("score") > 0]
                if sleep_scores:
                    summary["avg_sleep_score"] = sum(sleep_scores) / len(sleep_scores)
                
                # Latency analysis
                latencies = [d["data"].get("latency", 0) for d in sleep_data if d["data"].get("latency") is not None and d["data"].get("latency") >= 0]
                if latencies:
                    summary["avg_sleep_latency_minutes"] = sum(latencies) / len(latencies) / 60
            
            # Enhanced readiness analysis
            if readiness_data:
                readiness_scores = [d["data"].get("score", 0) for d in readiness_data if d["data"].get("score") is not None and d["data"].get("score") > 0]
                if readiness_scores:
                    summary["avg_readiness_score"] = sum(readiness_scores) / len(readiness_scores)
                
                # Temperature analysis
                temp_deviations = [d["data"].get("temperature_deviation", 0) for d in readiness_data if d["data"].get("temperature_deviation") is not None]
                if temp_deviations:
                    summary["avg_temperature_deviation"] = sum(temp_deviations) / len(temp_deviations)
            
            # Enhanced activity analysis with new fields
            if activity_data:
                # Basic metrics
                steps = [d["data"].get("steps", 0) for d in activity_data if d["data"].get("steps") is not None and d["data"].get("steps") > 0]
                if steps:
                    summary["avg_steps"] = sum(steps) / len(steps)
                    summary["total_steps"] = sum(steps)
                    summary["max_steps"] = max(steps)
                    summary["min_steps"] = min(steps)
                
                # Calorie analysis (use 'calories' or 'total_calories' field)
                total_calories = []
                for d in activity_data:
                    cal_val = d["data"].get("calories") or d["data"].get("total_calories")
                    if cal_val is not None and cal_val > 0:
                        total_calories.append(cal_val)
                
                active_calories = []
                for d in activity_data:
                    active_cal = d["data"].get("active_calories")
                    if active_cal is not None and active_cal > 0:
                        active_calories.append(active_cal)
                
                if total_calories:
                    summary["avg_total_calories"] = sum(total_calories) / len(total_calories)
                if active_calories:
                    summary["avg_active_calories"] = sum(active_calories) / len(active_calories)
                
                # Activity scores
                activity_scores = [d["data"].get("activity_score", 0) for d in activity_data if d["data"].get("activity_score") is not None and d["data"].get("activity_score") > 0]
                if activity_scores:
                    summary["avg_activity_score"] = sum(activity_scores) / len(activity_scores)
                
                # Goal tracking
                target_calories = [d["data"].get("target_calories", 0) for d in activity_data if d["data"].get("target_calories") is not None and d["data"].get("target_calories") > 0]
                if target_calories:
                    summary["avg_target_calories"] = sum(target_calories) / len(target_calories)
                
                # Time analysis
                resting_times = [d["data"].get("resting_time", 0) for d in activity_data if d["data"].get("resting_time") is not None and d["data"].get("resting_time") > 0]
                sedentary_times = [d["data"].get("sedentary_time", 0) for d in activity_data if d["data"].get("sedentary_time") is not None and d["data"].get("sedentary_time") > 0]
                
                if resting_times:
                    summary["avg_resting_time_hours"] = sum(resting_times) / len(resting_times) / 3600
                if sedentary_times:
                    summary["avg_sedentary_time_hours"] = sum(sedentary_times) / len(sedentary_times) / 3600
            
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
    
    def get_user_insights(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate comprehensive insights for a user using enhanced data"""
        try:
            user_id = self._get_user_id(user_id)
            # Get recent data
            end_date = date.today()
            start_date = end_date - timedelta(days=7)
            
            response = self.supabase.table("health_data").select("*").eq(
                "user_id", user_id
            ).gte("day", start_date.isoformat()).lte("day", end_date.isoformat()).execute()
            
            data = response.data
            
            insights = {
                "user_id": user_id,
                "period": "last_7_days",
                "insights": []
            }
            
            # Enhanced sleep pattern analysis
            sleep_data = [d for d in data if d["data_type"] == "sleep"]
            if sleep_data:
                # Sleep duration insights
                sleep_durations = [d["data"].get("total_sleep_duration", 0) for d in sleep_data]
                avg_sleep = sum(sleep_durations) / len(sleep_durations)
                avg_sleep_hours = avg_sleep / 3600
                
                if avg_sleep_hours < 7:
                    insights["insights"].append({
                        "type": "sleep",
                        "category": "duration",
                        "message": f"Average sleep duration is {avg_sleep_hours:.1f} hours, consider getting more sleep",
                        "severity": "warning",
                        "metric": "sleep_duration",
                        "value": avg_sleep_hours,
                        "recommendation": "Aim for 7-9 hours of sleep per night"
                    })
                elif avg_sleep_hours > 9:
                    insights["insights"].append({
                        "type": "sleep",
                        "category": "duration",
                        "message": f"Average sleep duration is {avg_sleep_hours:.1f} hours, this might be excessive",
                        "severity": "info",
                        "metric": "sleep_duration",
                        "value": avg_sleep_hours,
                        "recommendation": "Consider if you're getting enough quality sleep"
                    })
                
                # Sleep efficiency insights
                efficiencies = [d["data"].get("efficiency", 0) for d in sleep_data if d["data"].get("efficiency")]
                if efficiencies:
                    avg_efficiency = sum(efficiencies) / len(efficiencies)
                    if avg_efficiency < 85:
                        insights["insights"].append({
                            "type": "sleep",
                            "category": "efficiency",
                            "message": f"Sleep efficiency is {avg_efficiency:.1f}%, room for improvement",
                            "severity": "warning",
                            "metric": "sleep_efficiency",
                            "value": avg_efficiency,
                            "recommendation": "Improve sleep hygiene and reduce disturbances"
                        })
                    elif avg_efficiency > 95:
                        insights["insights"].append({
                            "type": "sleep",
                            "category": "efficiency",
                            "message": f"Excellent sleep efficiency at {avg_efficiency:.1f}%!",
                            "severity": "positive",
                            "metric": "sleep_efficiency",
                            "value": avg_efficiency
                        })
                
                # Sleep stage insights
                deep_sleep = [d["data"].get("deep_sleep_duration", 0) for d in sleep_data]
                rem_sleep = [d["data"].get("rem_sleep_duration", 0) for d in sleep_data]
                
                if deep_sleep:
                    avg_deep = sum(deep_sleep) / len(deep_sleep) / 3600
                    if avg_deep < 1.5:
                        insights["insights"].append({
                            "type": "sleep",
                            "category": "deep_sleep",
                            "message": f"Deep sleep is {avg_deep:.1f} hours, below recommended 1.5-2 hours",
                            "severity": "warning",
                            "metric": "deep_sleep_hours",
                            "value": avg_deep,
                            "recommendation": "Reduce stress and avoid late exercise"
                        })
                
                if rem_sleep:
                    avg_rem = sum(rem_sleep) / len(rem_sleep) / 3600
                    if avg_rem < 1.5:
                        insights["insights"].append({
                            "type": "sleep",
                            "category": "rem_sleep",
                            "message": f"REM sleep is {avg_rem:.1f} hours, below recommended 1.5-2 hours",
                            "severity": "warning",
                            "metric": "rem_sleep_hours",
                            "value": avg_rem,
                            "recommendation": "Ensure consistent sleep schedule"
                        })
                
                # Sleep score insights
                sleep_scores = [d["data"].get("score", 0) for d in sleep_data if d["data"].get("score")]
                if sleep_scores:
                    avg_score = sum(sleep_scores) / len(sleep_scores)
                    if avg_score < 70:
                        insights["insights"].append({
                            "type": "sleep",
                            "category": "score",
                            "message": f"Sleep score is {avg_score:.0f}, focus on sleep quality",
                            "severity": "warning",
                            "metric": "sleep_score",
                            "value": avg_score,
                            "recommendation": "Review sleep environment and routine"
                        })
            
            # Enhanced activity pattern analysis
            activity_data = [d for d in data if d["data_type"] == "activity"]
            if activity_data:
                # Steps analysis
                steps = [d["data"].get("steps", 0) for d in activity_data if d["data"].get("steps")]
                if steps:
                    avg_steps = sum(steps) / len(steps)
                    if avg_steps < 5000:
                        insights["insights"].append({
                            "type": "activity",
                            "category": "steps",
                            "message": f"Average daily steps is {avg_steps:.0f}, consider increasing activity",
                            "severity": "warning",
                            "metric": "daily_steps",
                            "value": avg_steps,
                            "recommendation": "Aim for 8,000-10,000 steps daily"
                        })
                    elif avg_steps > 12000:
                        insights["insights"].append({
                            "type": "activity",
                            "category": "steps",
                            "message": f"Great activity level with {avg_steps:.0f} average steps!",
                            "severity": "positive",
                            "metric": "daily_steps",
                            "value": avg_steps
                        })
                
                # Activity score insights
                activity_scores = [d["data"].get("activity_score", 0) for d in activity_data if d["data"].get("activity_score")]
                if activity_scores:
                    avg_activity_score = sum(activity_scores) / len(activity_scores)
                    if avg_activity_score < 70:
                        insights["insights"].append({
                            "type": "activity",
                            "category": "score",
                            "message": f"Activity score is {avg_activity_score:.0f}, room for improvement",
                            "severity": "warning",
                            "metric": "activity_score",
                            "value": avg_activity_score,
                            "recommendation": "Increase daily movement and exercise"
                        })
                
                # Calorie insights
                total_calories = [d["data"].get("total_calories", 0) for d in activity_data if d["data"].get("total_calories")]
                target_calories = [d["data"].get("target_calories", 0) for d in activity_data if d["data"].get("target_calories")]
                
                if total_calories and target_calories:
                    avg_calories = sum(total_calories) / len(total_calories)
                    avg_target = sum(target_calories) / len(target_calories)
                    
                    if avg_calories < avg_target * 0.8:
                        insights["insights"].append({
                            "type": "activity",
                            "category": "calories",
                            "message": f"Calorie burn ({avg_calories:.0f}) below target ({avg_target:.0f})",
                            "severity": "warning",
                            "metric": "calorie_burn",
                            "value": avg_calories,
                            "target": avg_target,
                            "recommendation": "Increase daily activity to meet calorie goals"
                        })
                    elif avg_calories > avg_target * 1.2:
                        insights["insights"].append({
                            "type": "activity",
                            "category": "calories",
                            "message": f"Exceeding calorie burn targets! ({avg_calories:.0f} vs {avg_target:.0f})",
                            "severity": "positive",
                            "metric": "calorie_burn",
                            "value": avg_calories,
                            "target": avg_target
                        })
                
                # Goal achievement insights
                meters_to_target = [d["data"].get("meters_to_target", 0) for d in activity_data if d["data"].get("meters_to_target")]
                if meters_to_target:
                    avg_meters = sum(meters_to_target) / len(meters_to_target)
                    if avg_meters < 0:  # Negative means exceeded target
                        insights["insights"].append({
                            "type": "activity",
                            "category": "goals",
                            "message": f"Exceeding daily distance targets by {abs(avg_meters):.0f} meters!",
                            "severity": "positive",
                            "metric": "meters_to_target",
                            "value": avg_meters
                        })
                    elif avg_meters > 2000:  # Far from target
                        insights["insights"].append({
                            "type": "activity",
                            "category": "goals",
                            "message": f"Daily distance target missed by {avg_meters:.0f} meters",
                            "severity": "warning",
                            "metric": "meters_to_target",
                            "value": avg_meters,
                            "recommendation": "Increase daily walking or exercise"
                        })
            
            # Readiness insights
            readiness_data = [d for d in data if d["data_type"] == "readiness"]
            if readiness_data:
                readiness_scores = [d["data"].get("score", 0) for d in readiness_data if d["data"].get("score")]
                if readiness_scores:
                    avg_readiness = sum(readiness_scores) / len(readiness_scores)
                    if avg_readiness < 70:
                        insights["insights"].append({
                            "type": "readiness",
                            "category": "score",
                            "message": f"Readiness score is {avg_readiness:.0f}, focus on recovery",
                            "severity": "warning",
                            "metric": "readiness_score",
                            "value": avg_readiness,
                            "recommendation": "Prioritize rest and recovery today"
                        })
                    elif avg_readiness > 90:
                        insights["insights"].append({
                            "type": "readiness",
                            "category": "score",
                            "message": f"Excellent readiness score of {avg_readiness:.0f}!",
                            "severity": "positive",
                            "metric": "readiness_score",
                            "value": avg_readiness
                        })
            
            return insights
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_data_quality_report(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate comprehensive data quality report"""
        try:
            user_id = self._get_user_id(user_id)
            # Get all user data
            response = self.supabase.table("health_data").select("*").eq("user_id", user_id).execute()
            data = response.data
            
            report = {
                "user_id": user_id,
                "total_records": len(data),
                "data_types": {},
                "data_quality": {},
                "field_completeness": {}
            }
            
            # Count by data type
            for record in data:
                data_type = record["data_type"]
                if data_type not in report["data_types"]:
                    report["data_types"][data_type] = 0
                report["data_types"][data_type] += 1
            
            # Check data quality and field completeness
            if data:
                dates = [datetime.fromisoformat(record["day"]).date() for record in data]
                date_range = max(dates) - min(dates)
                report["data_quality"]["date_range_days"] = date_range.days
                report["data_quality"]["data_frequency"] = len(data) / max(1, date_range.days)
                
                # Check field completeness for each data type
                for data_type in report["data_types"]:
                    type_records = [r for r in data if r["data_type"] == data_type]
                    if type_records:
                        # Get all possible fields from the first record
                        sample_data = type_records[0]["data"]
                        if isinstance(sample_data, dict):
                            field_completeness = {}
                            for field in sample_data.keys():
                                non_null_count = sum(1 for r in type_records if r["data"].get(field) is not None)
                                field_completeness[field] = {
                                    "total_records": len(type_records),
                                    "non_null_count": non_null_count,
                                    "completeness_percentage": (non_null_count / len(type_records)) * 100
                                }
                            report["field_completeness"][data_type] = field_completeness
            
            return report
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_sleep_analysis(self, user_id: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """Get detailed sleep analysis using enhanced data"""
        try:
            user_id = self._get_user_id(user_id)
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            response = self.supabase.table("health_data").select("*").eq(
                "user_id", user_id
            ).eq("data_type", "sleep").gte("day", start_date.isoformat()).lte("day", end_date.isoformat()).execute()
            
            sleep_data = response.data
            
            if not sleep_data:
                return {"error": "No sleep data found"}
            
            analysis = {
                "user_id": user_id,
                "period_days": days,
                "total_sleep_sessions": len(sleep_data),
                "sleep_metrics": {},
                "sleep_stages": {},
                "sleep_quality": {},
                "trends": {}
            }
            
            # Calculate comprehensive sleep metrics
            durations = [d["data"].get("total_sleep_duration", 0) for d in sleep_data]
            efficiencies = [d["data"].get("efficiency", 0) for d in sleep_data if d["data"].get("efficiency")]
            scores = [d["data"].get("score", 0) for d in sleep_data if d["data"].get("score")]
            latencies = [d["data"].get("latency", 0) for d in sleep_data if d["data"].get("latency")]
            
            if durations:
                analysis["sleep_metrics"]["avg_duration_hours"] = sum(durations) / len(durations) / 3600
                analysis["sleep_metrics"]["min_duration_hours"] = min(durations) / 3600
                analysis["sleep_metrics"]["max_duration_hours"] = max(durations) / 3600
            
            if efficiencies:
                analysis["sleep_quality"]["avg_efficiency"] = sum(efficiencies) / len(efficiencies)
                analysis["sleep_quality"]["min_efficiency"] = min(efficiencies)
                analysis["sleep_quality"]["max_efficiency"] = max(efficiencies)
            
            if scores:
                analysis["sleep_quality"]["avg_score"] = sum(scores) / len(scores)
                analysis["sleep_quality"]["min_score"] = min(scores)
                analysis["sleep_quality"]["max_score"] = max(scores)
            
            if latencies:
                analysis["sleep_quality"]["avg_latency_minutes"] = sum(latencies) / len(latencies) / 60
            
            # Sleep stage analysis
            deep_sleep = [d["data"].get("deep_sleep_duration", 0) for d in sleep_data]
            rem_sleep = [d["data"].get("rem_sleep_duration", 0) for d in sleep_data]
            light_sleep = [d["data"].get("light_sleep_duration", 0) for d in sleep_data]
            
            if deep_sleep:
                analysis["sleep_stages"]["deep_sleep_hours"] = sum(deep_sleep) / len(deep_sleep) / 3600
            if rem_sleep:
                analysis["sleep_stages"]["rem_sleep_hours"] = sum(rem_sleep) / len(rem_sleep) / 3600
            if light_sleep:
                analysis["sleep_stages"]["light_sleep_hours"] = sum(light_sleep) / len(light_sleep) / 3600
            
            return analysis
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_activity_analysis(self, user_id: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """Get detailed activity analysis using enhanced data"""
        try:
            user_id = self._get_user_id(user_id)
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            response = self.supabase.table("health_data").select("*").eq(
                "user_id", user_id
            ).eq("data_type", "activity").gte("day", start_date.isoformat()).lte("day", end_date.isoformat()).execute()
            
            activity_data = response.data
            
            if not activity_data:
                return {"error": "No activity data found"}
            
            analysis = {
                "user_id": user_id,
                "period_days": days,
                "total_activity_days": len(activity_data),
                "steps_analysis": {},
                "calorie_analysis": {},
                "goal_tracking": {},
                "time_analysis": {}
            }
            
            # Steps analysis
            steps = [d["data"].get("steps", 0) for d in activity_data if d["data"].get("steps")]
            if steps:
                analysis["steps_analysis"]["avg_steps"] = sum(steps) / len(steps)
                analysis["steps_analysis"]["total_steps"] = sum(steps)
                analysis["steps_analysis"]["max_steps"] = max(steps)
                analysis["steps_analysis"]["min_steps"] = min(steps)
                analysis["steps_analysis"]["step_consistency"] = len([s for s in steps if s >= 8000]) / len(steps) * 100
            
            # Calorie analysis
            total_calories = [d["data"].get("total_calories", 0) for d in activity_data if d["data"].get("total_calories")]
            active_calories = [d["data"].get("active_calories", 0) for d in activity_data if d["data"].get("active_calories")]
            
            if total_calories:
                analysis["calorie_analysis"]["avg_total_calories"] = sum(total_calories) / len(total_calories)
                analysis["calorie_analysis"]["total_calories_burned"] = sum(total_calories)
            
            if active_calories:
                analysis["calorie_analysis"]["avg_active_calories"] = sum(active_calories) / len(active_calories)
            
            # Goal tracking
            target_calories = [d["data"].get("target_calories", 0) for d in activity_data if d["data"].get("target_calories")]
            meters_to_target = [d["data"].get("meters_to_target", 0) for d in activity_data if d["data"].get("meters_to_target")]
            
            if target_calories:
                analysis["goal_tracking"]["avg_target_calories"] = sum(target_calories) / len(target_calories)
            
            if meters_to_target:
                analysis["goal_tracking"]["avg_meters_to_target"] = sum(meters_to_target) / len(meters_to_target)
                analysis["goal_tracking"]["goal_achievement_rate"] = len([m for m in meters_to_target if m <= 0]) / len(meters_to_target) * 100
            
            # Time analysis
            resting_times = [d["data"].get("resting_time", 0) for d in activity_data if d["data"].get("resting_time")]
            sedentary_times = [d["data"].get("sedentary_time", 0) for d in activity_data if d["data"].get("sedentary_time")]
            
            if resting_times:
                analysis["time_analysis"]["avg_resting_time_hours"] = sum(resting_times) / len(resting_times) / 3600
            
            if sedentary_times:
                analysis["time_analysis"]["avg_sedentary_time_hours"] = sum(sedentary_times) / len(sedentary_times) / 3600
            
            return analysis
            
        except Exception as e:
            return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    mcp = SupabaseMCP()
    
    # Example: Get comprehensive health summary for a user
    # summary = mcp.get_health_summary("user-uuid-here")
    # print(json.dumps(summary, indent=2))
    
    # Example: Get enhanced insights
    # insights = mcp.get_user_insights("user-uuid-here")
    # print(json.dumps(insights, indent=2))
    
    # Example: Get detailed sleep analysis
    # sleep_analysis = mcp.get_sleep_analysis("user-uuid-here")
    # print(json.dumps(sleep_analysis, indent=2))
    
    # Example: Get detailed activity analysis
    # activity_analysis = mcp.get_activity_analysis("user-uuid-here")
    # print(json.dumps(activity_analysis, indent=2))


