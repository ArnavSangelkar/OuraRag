#!/usr/bin/env python3
"""
Test script for Supabase MCP setup
Run this to verify your Supabase MCP configuration
"""

import os
import json
from dotenv import load_dotenv
from supabase_mcp import SupabaseMCP

def test_mcp_connection():
    """Test basic MCP connection"""
    try:
        print("🔧 Testing Supabase MCP connection...")
        mcp = SupabaseMCP()
        print("✅ Supabase MCP connection successful!")
        return True
    except Exception as e:
        print(f"❌ MCP connection failed: {e}")
        return False

def test_database_tables():
    """Test if required tables exist"""
    try:
        print("\n🔧 Testing database tables...")
        mcp = SupabaseMCP()
        
        # Test basic query to check if tables exist
        # This will fail if tables don't exist
        response = mcp.supabase.table("health_data").select("count", count="exact").limit(1).execute()
        print("✅ health_data table exists")
        
        response = mcp.supabase.table("vector_chunks").select("count", count="exact").limit(1).execute()
        print("✅ vector_chunks table exists")
        
        response = mcp.supabase.table("user_settings").select("count", count="exact").limit(1).execute()
        print("✅ user_settings table exists")
        
        return True
    except Exception as e:
        print(f"❌ Database table test failed: {e}")
        return False

def test_mcp_functions():
    """Test MCP functions with sample data"""
    try:
        print("\n🔧 Testing MCP functions...")
        mcp = SupabaseMCP()
        
        # Test with a dummy user ID (this will return empty results but won't error)
        test_user_id = "00000000-0000-0000-0000-000000000000"
        
        # Test health summary
        summary = mcp.get_health_summary(test_user_id, days=7)
        print("✅ get_health_summary function works")
        
        # Test user insights
        insights = mcp.get_user_insights(test_user_id)
        print("✅ get_user_insights function works")
        
        # Test data quality report
        report = mcp.get_data_quality_report(test_user_id)
        print("✅ get_data_quality_report function works")
        
        return True
    except Exception as e:
        print(f"❌ MCP function test failed: {e}")
        return False

def check_environment_variables():
    """Check if required environment variables are set"""
    print("🔧 Checking environment variables...")
    
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "OPENAI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            print(f"✅ {var} is set")
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Supabase MCP Setup Test")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Run tests
    tests = [
        ("Environment Variables", check_environment_variables),
        ("MCP Connection", test_mcp_connection),
        ("Database Tables", test_database_tables),
        ("MCP Functions", test_mcp_functions)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results Summary:")
    print("=" * 40)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your Supabase MCP is ready to use.")
        print("\nNext steps:")
        print("1. Add real user data to test with actual health records")
        print("2. Integrate MCP functions into your API endpoints")
        print("3. Use MCP in your Streamlit interface")
    else:
        print("\n⚠️  Some tests failed. Please check the setup guide in MCP_SETUP.md")
        print("\nCommon issues:")
        print("1. Missing environment variables in .env file")
        print("2. Database tables not created")
        print("3. Incorrect Supabase credentials")
        print("4. Network connectivity issues")

if __name__ == "__main__":
    main()
