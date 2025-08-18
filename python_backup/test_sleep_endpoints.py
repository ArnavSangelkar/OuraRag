#!/usr/bin/env python3
"""
Test different Oura sleep API endpoints
"""
import os
from datetime import date, timedelta
from dotenv import load_dotenv
from rich import print
import httpx

load_dotenv()

def test_sleep_endpoints():
    """Test different sleep API endpoints"""
    
    token = os.getenv("OURA_PERSONAL_ACCESS_TOKEN")
    if not token:
        print("❌ OURA_PERSONAL_ACCESS_TOKEN not set")
        return
    
    base_url = "https://api.ouraring.com/v2"
    headers = {"Authorization": f"Bearer {token}"}
    
    end = date.today()
    start = end - timedelta(days=7)
    
    # Test different sleep endpoints
    endpoints = [
        "/usercollection/daily_sleep",
        "/usercollection/sleep",
        "/sleep",
        "/daily_sleep"
    ]
    
    for endpoint in endpoints:
        print(f"\n🔍 Testing endpoint: {endpoint}")
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{base_url}{endpoint}",
                    headers=headers,
                    params={
                        "start_date": start.isoformat(),
                        "end_date": end.isoformat()
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Status: {response.status_code}")
                    print(f"📊 Response keys: {list(data.keys())}")
                    
                    if "data" in data:
                        sleep_records = data["data"]
                        print(f"📈 Sleep records: {len(sleep_records)}")
                        
                        if sleep_records:
                            # Show first record structure
                            first = sleep_records[0]
                            print(f"🔍 First record keys: {list(first.keys())}")
                            
                            # Check for sleep duration
                            if "total_sleep_duration" in first:
                                duration = first.get("total_sleep_duration")
                                print(f"⏰ Sleep duration: {duration}")
                            
                            if "sleep" in first:
                                sleep_data = first.get("sleep", {})
                                print(f"😴 Sleep data keys: {list(sleep_data.keys())}")
                    else:
                        print("❌ No 'data' key in response")
                        
                else:
                    print(f"❌ Status: {response.status_code}")
                    print(f"📝 Response: {response.text[:200]}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_sleep_endpoints()


