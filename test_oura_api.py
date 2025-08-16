#!/usr/bin/env python3
"""
Simple test script to verify Oura API is working
"""
import os
from datetime import date, timedelta
from dotenv import load_dotenv
from rich import print

# Load environment variables
load_dotenv()

# Import the Oura client
from app.oura_client import OuraClient

def test_oura_api():
    """Test the Oura API connection and data fetching"""
    
    # Check if token is set
    token = os.getenv("OURA_PERSONAL_ACCESS_TOKEN")
    if not token:
        print("[red]Error: OURA_PERSONAL_ACCESS_TOKEN not set in environment[/red]")
        print("Please set your Oura personal access token in a .env file or export it:")
        print("export OURA_PERSONAL_ACCESS_TOKEN='your_token_here'")
        return False
    
    try:
        print("[green]Testing Oura API connection...[/green]")
        
        # Create client
        client = OuraClient(token)
        print("✓ Oura client created successfully")
        
        # Set date range (last 7 days to avoid too much data)
        end = date.today()
        start = end - timedelta(days=7)
        
        print(f"Fetching data from {start} to {end}")
        
        # Test sleep data
        print("\n[blue]Testing sleep data fetch...[/blue]")
        sleep = client.fetch_sleep(start, end)
        print(f"✓ Sleep data: {len(sleep)} records fetched")
        if sleep:
            print(f"  Sample: {sleep[0]}")
        
        # Test readiness data
        print("\n[blue]Testing readiness data fetch...[/blue]")
        readiness = client.fetch_readiness(start, end)
        print(f"✓ Readiness data: {len(readiness)} records fetched")
        if readiness:
            print(f"  Sample: {readiness[0]}")
        
        # Test activity data
        print("\n[blue]Testing activity data fetch...[/blue]")
        activity = client.fetch_activity(start, end)
        print(f"✓ Activity data: {len(activity)} records fetched")
        if activity:
            print(f"  Sample: {activity[0]}")
        
        # Close client
        client.close()
        print("\n[green]✓ All API tests passed successfully![/green]")
        return True
        
    except Exception as e:
        print(f"\n[red]Error testing Oura API: {e}[/red]")
        return False

if __name__ == "__main__":
    test_oura_api()
