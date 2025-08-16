#!/usr/bin/env python3
"""
Streamlit Web App for Oura RAG System
Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import os
from datetime import date, timedelta
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load environment variables
load_dotenv()

# Import our app modules
from app.oura_client import OuraClient
from app.indexer import Indexer
from app.vectorstore import VectorStore
from app.ai_helper import ask_ai

# Page configuration
st.set_page_config(
    page_title="Oura Health Analytics",
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

def check_api_keys():
    """Check if required API keys are set"""
    oura_token = os.getenv("OURA_PERSONAL_ACCESS_TOKEN")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not oura_token:
        st.error("❌ OURA_PERSONAL_ACCESS_TOKEN not set. Please add it to your .env file.")
        return False
    
    if not openai_key:
        st.error("❌ OPENAI_API_KEY not set. Please add it to your .env file.")
        return False
    
    return True

def fetch_recent_data(days=7):
    """Fetch recent Oura data for display"""
    try:
        token = os.getenv("OURA_PERSONAL_ACCESS_TOKEN")
        client = OuraClient(token)
        
        end = date.today()
        start = end - timedelta(days=days)
        
        sleep = client.fetch_sleep(start, end)
        readiness = client.fetch_readiness(start, end)
        activity = client.fetch_activity(start, end)
        
        client.close()
        
        return sleep, readiness, activity
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None, None, None

def create_activity_chart(activity_data):
    """Create a steps chart"""
    if not activity_data:
        return None
    
    df = pd.DataFrame([{
        'date': str(act.day),
        'steps': act.steps or 0,
        'active_calories': act.active_calories or 0,
        'total_calories': act.total_calories or 0
    } for act in activity_data])
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Daily Steps', 'Daily Calories'),
        vertical_spacing=0.1
    )
    
    fig.add_trace(
        go.Bar(x=df['date'], y=df['steps'], name='Steps', marker_color='#1f77b4'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=df['date'], y=df['active_calories'], name='Active Calories', marker_color='#ff7f0e'),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Bar(x=df['date'], y=df['total_calories'], name='Total Calories', marker_color='#2ca02c'),
        row=2, col=1
    )
    
    fig.update_layout(height=500, showlegend=True)
    return fig

def create_readiness_chart(readiness_data):
    """Create a readiness score chart"""
    if not readiness_data:
        return None
    
    df = pd.DataFrame([{
        'date': str(ready.day),
        'score': ready.score or 0
    } for ready in readiness_data])
    
    fig = px.line(df, x='date', y='score', 
                  title='Daily Readiness Scores',
                  markers=True)
    
    fig.update_layout(height=400)
    fig.update_traces(line=dict(width=3, color='#1f77b4'))
    
    return fig

def main():
    # Header
    st.markdown('<h1 class="main-header">💍 Oura Health Analytics</h1>', unsafe_allow_html=True)
    
    # Check API keys
    if not check_api_keys():
        st.stop()
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Dashboard", "📊 Data Sync", "🤖 AI Chat", "📈 Analytics"]
    )
    
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "📊 Data Sync":
        show_data_sync()
    elif page == "🤖 AI Chat":
        show_ai_chat()
    elif page == "📈 Analytics":
        show_analytics()

def show_dashboard():
    """Show the main dashboard"""
    st.header("📊 Health Dashboard")
    
    # Fetch recent data
    with st.spinner("Fetching your latest health data..."):
        sleep, readiness, activity = fetch_recent_data(7)
    
    if not all([sleep, readiness, activity]):
        st.error("Failed to fetch data. Please check your Oura API connection.")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_steps = sum(act.steps or 0 for act in activity) / len(activity) if activity else 0
        st.metric("Average Steps (7 days)", f"{avg_steps:,.0f}")
    
    with col2:
        avg_readiness = sum(ready.score or 0 for ready in readiness) / len(readiness) if readiness else 0
        st.metric("Average Readiness", f"{avg_readiness:.1f}")
    
    with col3:
        total_sleep = sum(s.total_sleep_duration or 0 for s in sleep) / len(sleep) if sleep else 0
        st.metric("Average Sleep (min)", f"{total_sleep:.0f}")
    
    with col4:
        active_days = sum(1 for act in activity if (act.steps or 0) > 10000)
        st.metric("10K+ Step Days", f"{active_days}")
    
    # Charts
    st.subheader("📈 Activity Overview")
    activity_chart = create_activity_chart(activity)
    if activity_chart:
        st.plotly_chart(activity_chart, use_container_width=True)
    
    st.subheader("🎯 Readiness Trends")
    readiness_chart = create_readiness_chart(readiness)
    if readiness_chart:
        st.plotly_chart(readiness_chart, use_container_width=True)
    
    # Recent data table
    st.subheader("📋 Recent Data Summary")
    
    # Activity table
    if activity:
        activity_df = pd.DataFrame([{
            'Date': str(act.day),
            'Steps': act.steps or 0,
            'Active Calories': act.active_calories or 0,
            'Total Calories': act.total_calories or 0
        } for act in activity])
        st.dataframe(activity_df, use_container_width=True)

def show_data_sync():
    """Show data synchronization page"""
    st.header("📊 Data Synchronization")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("Sync your Oura data to the local vector database for AI-powered analysis.")
        
        days = st.slider("Days to sync:", min_value=7, max_value=365, value=30, step=7)
        
        if st.button("🔄 Sync Data", type="primary"):
            with st.spinner(f"Syncing {days} days of data..."):
                try:
                    indexer = Indexer()
                    indexer.sync(days=days)
                    st.success(f"✅ Successfully synced {days} days of data!")
                except Exception as e:
                    st.error(f"❌ Error syncing data: {e}")
    
    with col2:
        st.info("""
        **What gets synced:**
        - Sleep data
        - Readiness scores
        - Activity metrics
        
        **Storage:** Local ChromaDB vector database
        """)

def show_ai_chat():
    """Show AI chat interface"""
    st.header("🤖 AI Health Assistant")
    
    st.write("Ask questions about your health data in natural language!")
    
    # Question input
    question = st.text_input(
        "Ask a question about your health data:",
        placeholder="e.g., How did my sleep quality correlate with readiness scores?"
    )
    
    if st.button("🚀 Ask AI", type="primary") and question:
        with st.spinner("AI is analyzing your data..."):
            try:
                # Use the new AI helper function
                response = ask_ai(question)
                
                # Display response
                st.subheader("🤖 AI Response")
                st.write(response)
                
            except Exception as e:
                st.error(f"❌ Error getting AI response: {e}")
    
    # Example questions
    st.subheader("💡 Example Questions")
    examples = [
        "How many steps did I average this week?",
        "What was my highest readiness score this month?",
        "How did my activity level correlate with sleep quality?",
        "What's my sleep duration trend?",
        "Which days did I have the best recovery?"
    ]
    
    for example in examples:
        if st.button(example, key=example):
            st.session_state.example_question = example
            st.rerun()

def show_analytics():
    """Show detailed analytics"""
    st.header("📈 Detailed Analytics")
    
    # Date range selector
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("Start Date", value=date.today() - timedelta(days=30))
    
    with col2:
        end_date = st.date_input("End Date", value=date.today())
    
    if st.button("📊 Generate Analytics"):
        with st.spinner("Generating analytics..."):
            try:
                # Fetch data for the selected range
                token = os.getenv("OURA_PERSONAL_ACCESS_TOKEN")
                client = OuraClient(token)
                
                sleep = client.fetch_sleep(start_date, end_date)
                readiness = client.fetch_readiness(start_date, end_date)
                activity = client.fetch_activity(start_date, end_date)
                
                client.close()
                
                # Display analytics
                if sleep and readiness and activity:
                    st.success(f"✅ Analyzed {len(sleep)} days of data")
                    
                    # Sleep analytics
                    st.subheader("😴 Sleep Analytics")
                    sleep_df = pd.DataFrame([{
                        'Date': str(s.day),
                        'Duration (min)': s.total_sleep_duration or 0,
                        'Efficiency': s.efficiency or 0,
                        'Deep Sleep (min)': s.deep_sleep_duration or 0,
                        'REM Sleep (min)': s.rem_sleep_duration or 0
                    } for s in sleep])
                    
                    st.dataframe(sleep_df, use_container_width=True)
                    
                    # Readiness analytics
                    st.subheader("🎯 Readiness Analytics")
                    readiness_df = pd.DataFrame([{
                        'Date': str(r.day),
                        'Score': r.score or 0
                    } for r in readiness])
                    
                    st.dataframe(readiness_df, use_container_width=True)
                    
                else:
                    st.warning("No data available for the selected date range.")
                    
            except Exception as e:
                st.error(f"❌ Error generating analytics: {e}")

if __name__ == "__main__":
    main()
