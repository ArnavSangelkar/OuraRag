from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional

import httpx
from pydantic import BaseModel

OURA_BASE_URL = "https://api.ouraring.com/v2"

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
        raw = self._paginate(
            "/usercollection/sleep", start_date, end_date, items_key="data"
        )
        parsed: List[SleepSummary] = []
        for item in raw:
            parsed.append(
                SleepSummary(
                    day=date.fromisoformat(item["day"]),
                    total_sleep_duration=item.get("total_sleep_duration", 0),
                    score=item.get("score"),
                    efficiency=item.get("efficiency"),
                    latency=item.get("latency"),
                    deep_sleep_duration=item.get("deep_sleep_duration"),
                    rem_sleep_duration=item.get("rem_sleep_duration"),
                    light_sleep_duration=item.get("light_sleep_duration"),
                    average_breath=item.get("average_breath"),
                    average_heart_rate=item.get("average_heart_rate"),
                    average_hrv=item.get("hrv_average") or item.get("average_hrv"),
                    resting_heart_rate=item.get("resting_heart_rate"),
                )
            )
        return parsed

    def fetch_readiness(self, start_date: date, end_date: date) -> List[ReadinessSummary]:
        raw = self._paginate(
            "/usercollection/daily_readiness", start_date, end_date, items_key="data"
        )
        parsed: List[ReadinessSummary] = []
        for item in raw:
            parsed.append(ReadinessSummary(
                day=date.fromisoformat(item["day"]), 
                score=item.get("score"),
                average_hrv=item.get("hrv_average") or item.get("average_hrv"),
                resting_heart_rate=item.get("resting_heart_rate"),
                temperature_deviation=item.get("temperature_deviation")
            ))
        return parsed

    def fetch_activity(self, start_date: date, end_date: date) -> List[ActivitySummary]:
        raw = self._paginate(
            "/usercollection/daily_activity", start_date, end_date, items_key="data"
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

    def close(self) -> None:
        self._client.close()

