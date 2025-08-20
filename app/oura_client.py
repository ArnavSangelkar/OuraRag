from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional

import httpx
from pydantic import BaseModel

OURA_BASE_URL = "https://api.ouraring.com"

class SleepSummary(BaseModel):
    day: date
    total_sleep_duration: int
    score: Optional[int] = None
    efficiency: Optional[float] = None
    latency: Optional[int] = None
    deep_sleep_duration: Optional[int] = None
    rem_sleep_duration: Optional[int] = None
    light_sleep_duration: Optional[int] = None
    average_breath: Optional[float] = None
    average_heart_rate: Optional[float] = None
    average_hrv: Optional[float] = None
    resting_heart_rate: Optional[float] = None

class ReadinessSummary(BaseModel):
    day: date
    score: Optional[int] = None
    average_hrv: Optional[float] = None
    resting_heart_rate: Optional[int] = None
    temperature_deviation: Optional[float] = None

class ActivitySummary(BaseModel):
    day: date
    steps: Optional[int] = None
    inactive_time: Optional[int] = None
    active_calories: Optional[int] = None
    total_calories: Optional[int] = None
    average_met: Optional[float] = None

class SpO2Summary(BaseModel):
    day: date
    average_spo2: Optional[float] = None
    lowest_spo2: Optional[float] = None
    spo2_drops: Optional[int] = None

class HeartRateSummary(BaseModel):
    day: date
    average_heart_rate: Optional[float] = None
    resting_heart_rate: Optional[float] = None
    max_heart_rate: Optional[float] = None
    min_heart_rate: Optional[float] = None

class OuraClient:
    def __init__(self, access_token: str, timeout_seconds: float = 30.0) -> None:
        self._access_token = access_token
        self._client = httpx.Client(
            base_url=OURA_BASE_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
            },
            timeout=timeout_seconds,
        )

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        response = self._client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    def _paginate(self, path: str, start_date: date, end_date: date, items_key: str) -> List[Dict[str, Any]]:
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "page_size": 200,
        }
        items: List[Dict[str, Any]] = []
        next_token: Optional[str] = None
        while True:
            q = params.copy()
            if next_token:
                q["next_token"] = next_token
            data = self._get(path, params=q)
            items.extend(data.get(items_key, []))
            next_token = data.get("next_token")
            if not next_token:
                break
        return items

    def fetch_sleep(self, start_date: date, end_date: date) -> List[SleepSummary]:
        # Get detailed sleep data from sleep sessions endpoint
        sleep_sessions = self._paginate(
            "/v2/usercollection/sleep", start_date, end_date, items_key="data"
        )
        
        # Get sleep scores from daily sleep endpoint
        daily_sleep = self._paginate(
            "/v2/usercollection/daily_sleep", start_date, end_date, items_key="data"
        )
        
        # Create a mapping of day -> score for easy lookup
        score_map = {item["day"]: item.get("score") for item in daily_sleep}
        
        parsed: List[SleepSummary] = []
        for item in sleep_sessions:
            # Debug: Print raw sleep data to see what's available
            print(f"🔍 Raw sleep data: {item.keys()}")
            
            # Get the score for this day
            day_score = score_map.get(item["day"])
            
            parsed.append(
                SleepSummary(
                    day=date.fromisoformat(item["day"]),
                    total_sleep_duration=item.get("total_sleep_duration", 0),
                    score=day_score,  # Use score from daily sleep endpoint
                    efficiency=item.get("efficiency") or item.get("sleep_efficiency"),
                    latency=item.get("latency") or item.get("sleep_latency"),
                    deep_sleep_duration=item.get("deep_sleep_duration") or item.get("deep_sleep"),
                    rem_sleep_duration=item.get("rem_sleep_duration") or item.get("rem_sleep"),
                    light_sleep_duration=item.get("light_sleep_duration") or item.get("light_sleep"),
                    average_breath=extract_numeric_value(item.get("average_breath") or item.get("breath_rate")),
                    average_heart_rate=extract_numeric_value(item.get("average_heart_rate") or item.get("heart_rate")),
                    average_hrv=extract_numeric_value(item.get("hrv_average") or item.get("average_hrv") or item.get("hrv")),
                    resting_heart_rate=extract_numeric_value(item.get("resting_heart_rate") or item.get("rest_heart_rate")),
                )
            )
        return parsed

    def fetch_readiness(self, start_date: date, end_date: date) -> List[ReadinessSummary]:
        raw = self._paginate(
            "/v2/usercollection/daily_readiness", start_date, end_date, items_key="data"
        )
        parsed: List[ReadinessSummary] = []
        for item in raw:
            # Debug: Print raw readiness data to see what's available
            print(f"🔍 Raw readiness data: {item.keys()}")
            
            parsed.append(ReadinessSummary(
                day=date.fromisoformat(item["day"]), 
                score=item.get("score") or item.get("readiness_score"),
                average_hrv=extract_numeric_value(item.get("hrv_average") or item.get("average_hrv") or item.get("hrv") or item.get("hrv_balance")),
                resting_heart_rate=extract_numeric_value(item.get("resting_heart_rate") or item.get("rest_heart_rate") or item.get("heart_rate")),
                temperature_deviation=extract_numeric_value(item.get("temperature_deviation") or item.get("temperature"))
            ))
        return parsed

    def fetch_activity(self, start_date: date, end_date: date) -> List[ActivitySummary]:
        raw = self._paginate(
            "/v2/usercollection/daily_activity", start_date, end_date, items_key="data"
        )
        parsed: List[ActivitySummary] = []
        for item in raw:
            parsed.append(
                ActivitySummary(
                    day=date.fromisoformat(item["day"]),
                    steps=item.get("steps"),
                    inactive_time=item.get("inactive_time"),
                    active_calories=item.get("active_calories"),
                    total_calories=item.get("total_calories"),
                    average_met=item.get("average_met"),
                )
            )
        return parsed

    def fetch_spo2(self, start_date: date, end_date: date) -> List[SpO2Summary]:
        """Fetch SpO2 (blood oxygen) data"""
        raw = self._paginate(
            "/v2/usercollection/daily_spo2", start_date, end_date, items_key="data"
        )
        parsed: List[SpO2Summary] = []
        for item in raw:
            parsed.append(
                SpO2Summary(
                    day=date.fromisoformat(item["day"]),
                    average_spo2=extract_numeric_value(item.get("average_spo2") or item.get("spo2_average")),
                    lowest_spo2=extract_numeric_value(item.get("lowest_spo2") or item.get("spo2_min")),
                    spo2_drops=item.get("spo2_drops") or item.get("drops_count"),
                )
            )
        return parsed

    def fetch_heart_rate(self, start_date: date, end_date: date) -> List[HeartRateSummary]:
        """Fetch heart rate data"""
        raw = self._paginate(
            "/v2/usercollection/heart_rate", start_date, end_date, items_key="data"
        )
        parsed: List[HeartRateSummary] = []
        for item in raw:
            parsed.append(
                HeartRateSummary(
                    day=date.fromisoformat(item["day"]),
                    average_heart_rate=extract_numeric_value(item.get("average_heart_rate") or item.get("heart_rate_average")),
                    resting_heart_rate=extract_numeric_value(item.get("resting_heart_rate") or item.get("rest_heart_rate")),
                    max_heart_rate=extract_numeric_value(item.get("max_heart_rate") or item.get("heart_rate_max")),
                    min_heart_rate=extract_numeric_value(item.get("min_heart_rate") or item.get("heart_rate_min")),
                )
            )
        return parsed

    def close(self) -> None:
        self._client.close()


def extract_numeric_value(data: Any, default: float = 0.0) -> float:
    """Extract numeric value from Oura API response data"""
    if data is None:
        return default
    
    # If it's already a number, return it
    if isinstance(data, (int, float)):
        return float(data)
    
    # If it's a dict with time-series data, try to extract average
    if isinstance(data, dict):
        # Try common field names for averages
        for field in ['average', 'mean', 'value', 'hrv', 'heart_rate']:
            if field in data and isinstance(data[field], (int, float)):
                return float(data[field])
        
        # If no average field, try to calculate from items if available
        if 'items' in data and isinstance(data['items'], list):
            items = data['items']
            if items and all(isinstance(item, dict) and 'value' in item for item in items):
                values = [float(item['value']) for item in items if isinstance(item.get('value'), (int, float))]
                if values:
                    return sum(values) / len(values)
    
    # If it's a list, try to get the first numeric value
    if isinstance(data, list) and data:
        first_item = data[0]
        if isinstance(first_item, dict) and 'value' in first_item:
            return float(first_item['value'])
    
    return default

