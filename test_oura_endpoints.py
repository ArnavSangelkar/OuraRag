#!/usr/bin/env python3
"""
Test script to verify Oura API v2 endpoints are working correctly
"""

import os
from datetime import date, timedelta
from dotenv import load_dotenv
from app.oura_client import OuraClient

# Load environment variables
load_dotenv()

def test_oura_endpoints():
    """Test all Oura API v2 endpoints"""
    token = os.getenv("OURA_PERSONAL_ACCESS_TOKEN")
    if not token:
        print("❌ OURA_PERSONAL_ACCESS_TOKEN not set in .env file")
        return
    
    print("🔑 Testing Oura API v2 endpoints...")
    print(f"📅 Testing data for last 7 days")
    
    client = OuraClient(token)
    end = date.today()
    start = end - timedelta(days=7)
    
    try:
        # Test sleep endpoint
        print("\n🌙 Testing /v2/usercollection/daily_sleep...")
        sleep_data = client.fetch_sleep(start, end)
        print(f"✅ Sleep data: {len(sleep_data)} records")
        if sleep_data:
            print(f"   Sample: Day {sleep_data[0].day}, Score: {getattr(sleep_data[0], 'score', 'N/A')}")
        
        # Test readiness endpoint
        print("\n💪 Testing /v2/usercollection/daily_readiness...")
        readiness_data = client.fetch_readiness(start, end)
        print(f"✅ Readiness data: {len(readiness_data)} records")
        if readiness_data:
            print(f"   Sample: Day {readiness_data[0].day}, Score: {getattr(readiness_data[0], 'score', 'N/A')}")
        
        # Test activity endpoint
        print("\n🚶 Testing /v2/usercollection/daily_activity...")
        activity_data = client.fetch_activity(start, end)
        print(f"✅ Activity data: {len(activity_data)} records")
        if activity_data:
            print(f"   Sample: Day {activity_data[0].day}, Steps: {getattr(activity_data[0], 'steps', 'N/A')}")
        
        # Test SpO2 endpoint
        print("\n🫁 Testing /v2/usercollection/daily_spo2...")
        try:
            spo2_data = client.fetch_spo2(start, end)
            print(f"✅ SpO2 data: {len(spo2_data)} records")
            if spo2_data:
                print(f"   Sample: Day {spo2_data[0].day}, Avg SpO2: {getattr(spo2_data[0], 'average_spo2', 'N/A')}")
        except Exception as e:
            print(f"⚠️ SpO2 endpoint: {e}")
        
        # Test heart rate endpoint
        print("\n💓 Testing /v2/usercollection/heart_rate...")
        try:
            hr_data = client.fetch_heart_rate(start, end)
            print(f"✅ Heart rate data: {len(hr_data)} records")
            if hr_data:
                print(f"   Sample: Day {hr_data[0].day}, Avg HR: {getattr(hr_data[0], 'average_heart_rate', 'N/A')}")
        except Exception as e:
            print(f"⚠️ Heart rate endpoint: {e}")
        
        print("\n🎉 All endpoint tests completed!")
        
    except Exception as e:
        print(f"❌ Error testing endpoints: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    test_oura_endpoints()
