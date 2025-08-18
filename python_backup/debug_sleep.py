#!/usr/bin/env python3
"""
Debug script to investigate sleep data issues
"""
import os
from datetime import date, timedelta
from dotenv import load_dotenv
from rich import print

load_dotenv()

from app.oura_client import OuraClient

def debug_sleep_data():
    """Debug sleep data fetching"""
    
    token = os.getenv("OURA_PERSONAL_ACCESS_TOKEN")
    if not token:
        print("❌ OURA_PERSONAL_ACCESS_TOKEN not set")
        return
    
    try:
        client = OuraClient(token)
        
        # Test different date ranges
        end = date.today()
        
        # Last 7 days
        start_7 = end - timedelta(days=7)
        print(f"\n🔍 Testing sleep data for {start_7} to {end}")
        
        sleep_7 = client.fetch_sleep(start_7, end)
        print(f"📊 Sleep records: {len(sleep_7)}")
        
        for s in sleep_7:
            print(f"  {s.day}: Duration={s.total_sleep_duration}min, Efficiency={s.efficiency}, Deep={s.deep_sleep_duration}min, REM={s.rem_sleep_duration}min")
        
        # Last 30 days
        start_30 = end - timedelta(days=30)
        print(f"\n🔍 Testing sleep data for {start_30} to {end}")
        
        sleep_30 = client.fetch_sleep(start_30, end)
        print(f"📊 Sleep records: {len(sleep_30)}")
        
        # Show non-zero sleep days
        non_zero_sleep = [s for s in sleep_30 if s.total_sleep_duration and s.total_sleep_duration > 0]
        print(f"✅ Days with actual sleep data: {len(non_zero_sleep)}")
        
        for s in non_zero_sleep:
            print(f"  {s.day}: Duration={s.total_sleep_duration}min, Efficiency={s.efficiency}")
        
        # Test readiness and activity for comparison
        print(f"\n🔍 Testing readiness data for {start_7} to {end}")
        readiness = client.fetch_readiness(start_7, end)
        print(f"📊 Readiness records: {len(readiness)}")
        
        print(f"\n🔍 Testing activity data for {start_7} to {end}")
        activity = client.fetch_activity(start_7, end)
        print(f"📊 Activity records: {len(activity)}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_sleep_data()


