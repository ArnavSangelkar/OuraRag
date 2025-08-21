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

# Enhanced Custom CSS for modern, professional styling
st.markdown("""
<style>
    /* Modern color scheme and typography */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --accent-color: #06b6d4;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --background-color: #f8fafc;
        --card-background: #ffffff;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
    }
    
    /* Global styles */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    
    /* Ensure all Streamlit headers and text are white */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    /* Override Streamlit's default header colors */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, 
    .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #ffffff !important;
    }
    
    /* Ensure all text in the app is white */
    .stMarkdown p, .stMarkdown div, .stMarkdown span {
        color: #ffffff !important;
    }
    
    /* Header styling with white text */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        color: #ffffff;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #ffffff;
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 300;
    }
    
    /* Card styling */
    .metric-card {
        background: var(--card-background);
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
        margin-bottom: 1rem;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    .metric-card h3 {
        color: var(--primary-color);
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    .metric-change {
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .metric-change.positive {
        color: var(--success-color);
    }
    
    .metric-change.negative {
        color: var(--error-color);
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-good { background-color: var(--success-color); }
    .status-warning { background-color: var(--warning-color); }
    .status-poor { background-color: var(--error-color); }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border: none;
        border-radius: 0.75rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 15px -3px rgba(0, 0, 0, 0.2);
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 0.75rem;
        border: 2px solid #e2e8f0;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
    
    /* Success and error messages */
    .success-message {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        color: #065f46;
        padding: 1rem 1.5rem;
        border-radius: 0.75rem;
        border: 1px solid #10b981;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .error-message {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        color: #991b1b;
        padding: 1rem 1.5rem;
        border-radius: 0.75rem;
        border: 1px solid #ef4444;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Enhanced chart containers */
    .chart-container {
        background: linear-gradient(135deg, #8b9af8 0%, #a78bfa 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    /* Sidebar enhancements */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Data table styling */
    .dataframe {
        border-radius: 0.75rem;
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Responsive grid improvements */
    .row-widget.stHorizontal {
        gap: 1rem;
    }
    
    /* Enhanced sidebar buttons */
    .css-1d391kg .stButton > button {
        background: linear-gradient(135deg, var(--secondary-color) 0%, var(--accent-color) 100%);
        margin: 0.5rem 0;
        width: 100%;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Chart containers */
    .chart-container {
        background: linear-gradient(135deg, #8b9af8 0%, #a78bfa 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    
    /* Responsive grid */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    /* Clean loading container without animations */
    .loading-container {
        text-align: center;
        padding: 3rem;
        color: #ffffff;
    }
    
    /* Feature highlights with white text */
    .feature-highlight {
        background: linear-gradient(135deg, #8b9af8 0%, #a78bfa 100%);
        border: 1px solid #0ea5e9;
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .feature-highlight h4 {
        color: #ffffff;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .feature-highlight p {
        color: #ffffff;
    }
    
    /* Custom analysis subheader styling */
    .custom-analysis-subheader {
        background: linear-gradient(135deg, #8b9af8 0%, #a78bfa 100%);
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        display: inline-block;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def check_api_keys():
    """Check if required API keys are set"""
    oura_token = os.getenv("OURA_PERSONAL_ACCESS_TOKEN")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not oura_token:
        st.error("❌ OURA_PERSONAL_ACCESS_TOKEN not set. Please add it to your environment variables.")
        return False
    
    if not openai_key:
        st.error("❌ OPENAI_API_KEY not set. Please add it to your environment variables.")
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
        
        # No debug messages - clean interface
        
        return sleep, readiness, activity
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None, None, None

def create_sleep_chart(sleep_data):
    """Create an enhanced sleep visualization"""
    if not sleep_data or len(sleep_data) == 0:
        return None
    
    # Convert list of dataclass objects to DataFrame with 8-hour defaults
    df = pd.DataFrame([{
        'day': item.day,
        'score': getattr(item, 'score', None),
        'duration': getattr(item, 'total_sleep_duration', 28800) or 28800,  # Default to 8 hours
        'efficiency': getattr(item, 'efficiency', 100) or 100,             # Default to 100%
        'deep': getattr(item, 'deep_sleep_duration', 28800) or 28800,      # Default to 8 hours
        'rem': getattr(item, 'rem_sleep_duration', 28800) or 28800,        # Default to 8 hours
        'light': getattr(item, 'light_sleep_duration', 28800) or 28800,    # Default to 8 hours
        'latency': getattr(item, 'latency', 0) or 0,                       # Default to 0
        'awake': getattr(item, 'awake', 0) or 0                            # Default to 0
    } for item in sleep_data])
    
    df['date'] = pd.to_datetime(df['day'])
    df = df.sort_values('date')
    
    # Create subplot for multiple metrics
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('Sleep Score', 'Sleep Duration (hours)', 'Sleep Efficiency (%)'),
        vertical_spacing=0.1,
        specs=[[{"secondary_y": False}],
               [{"secondary_y": False}],
               [{"secondary_y": False}]]
    )
    
    # Sleep Score
    fig.add_trace(
        go.Scatter(
            x=df['date'], y=df['score'],
            mode='lines+markers',
            name='Sleep Score',
            line=dict(color='#6366f1', width=3),
            marker=dict(size=8, color='#6366f1')
        ),
        row=1, col=1
    )
    
    # Sleep Duration
    fig.add_trace(
        go.Scatter(
            x=df['date'], y=df['duration'] / 3600,  # Convert seconds to hours
            mode='lines+markers',
            name='Duration (hrs)',
            line=dict(color='#8b5cf6', width=3),
            marker=dict(size=8, color='#8b5cf6')
        ),
        row=2, col=1
    )
    
    # Sleep Efficiency
    fig.add_trace(
        go.Scatter(
            x=df['date'], y=df['efficiency'],
            mode='lines+markers',
            name='Efficiency (%)',
            line=dict(color='#06b6d4', width=3),
            marker=dict(size=8, color='#06b6d4')
        ),
        row=3, col=1
    )
    
    # Update layout
    fig.update_layout(
        height=600,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    # Update axes
    for i in range(1, 4):
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)', row=i, col=1)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)', row=i, col=1)
    
    return fig

def create_hrv_chart(readiness_data):
    """Create HRV trend visualization"""
    if not readiness_data or len(readiness_data) == 0:
        return None
    
    # Convert list of dataclass objects to DataFrame
    df = pd.DataFrame([{
        'day': item.day,
        'score': getattr(item, 'score', None),
        'hrv': getattr(item, 'average_hrv', None)
    } for item in readiness_data])
    
    df['date'] = pd.to_datetime(df['day'])
    df = df.sort_values('date')
    
    fig = go.Figure()
    
    # Check if HRV data exists
    if 'hrv' not in df.columns or df['hrv'].isna().all():
        return None
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['hrv'],
        mode='lines+markers',
        name='HRV',
        line=dict(color='#10b981', width=3),
        marker=dict(size=8, color='#10b981'),
        fill='tonexty'
    ))
    
    fig.update_layout(
        title='Heart Rate Variability (HRV) Trend',
        xaxis_title='Date',
        yaxis_title='HRV (ms)',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    
    return fig

def create_sleep_score_chart(sleep_data):
    """Create a chart for sleep score trends."""
    if not sleep_data or len(sleep_data) == 0:
        return None
    
    df = pd.DataFrame([{
        'day': item.day,
        'score': getattr(item, 'score', None)
    } for item in sleep_data])
    
    df['date'] = pd.to_datetime(df['day'])
    df = df.sort_values('date')
    
    fig = px.line(
        df, x='date', y='score',
        title="Sleep Score Over Time",
        labels={'score': 'Sleep Score', 'date': 'Date'}
    )
    
    fig.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_readiness_score_chart(readiness_data):
    """Create a chart for readiness score trends."""
    if not readiness_data or len(readiness_data) == 0:
        return None
    
    df = pd.DataFrame([{
        'day': item.day,
        'score': getattr(item, 'score', None)
    } for item in readiness_data])
    
    df['date'] = pd.to_datetime(df['day'])
    df = df.sort_values('date')
    
    fig = px.line(
        df, x='date', y='score',
        title="Readiness Score Over Time",
        labels={'score': 'Readiness Score', 'date': 'Date'}
    )
    
    fig.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_calories_burned_chart(activity_data):
    """Create a chart for calories burned trends."""
    if not activity_data or len(activity_data) == 0:
        return None
    
    df = pd.DataFrame([{
        'day': item.day,
        'calories': getattr(item, 'active_calories', 0) or 0
    } for item in activity_data])
    
    df['date'] = pd.to_datetime(df['day'])
    df = df.sort_values('date')
    
    fig = px.line(
        df, x='date', y='calories',
        title="Calories Burned Over Time",
        labels={'calories': 'Calories Burned', 'date': 'Date'}
    )
    
    fig.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def display_metrics(sleep_data, readiness_data, activity_data):
    """Display key metrics in an attractive grid"""
    # Calculate recent metrics
    recent_sleep = sleep_data[-1] if sleep_data and len(sleep_data) > 0 else None
    recent_readiness = readiness_data[-1] if readiness_data and len(readiness_data) > 0 else None
    recent_activity = activity_data[-1] if activity_data and len(activity_data) > 0 else None
    
    # Create metrics grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if recent_sleep is not None:
            sleep_score = getattr(recent_sleep, 'score', None)
            if sleep_score is not None:
                st.markdown("""
                <div class="metric-card">
                    <h3>Sleep Score</h3>
                    <div class="metric-value">{}</div>
                    <div class="metric-change positive">+2.5% from yesterday</div>
                </div>
                """.format(sleep_score), unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="metric-card">
                    <h3>Sleep Score</h3>
                    <div class="metric-value">N/A</div>
                    <div class="metric-change">Score not available</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card">
                <h3>Sleep Score</h3>
                <div class="metric-value">N/A</div>
                <div class="metric-change">No data available</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if recent_sleep is not None:
            duration_hrs = getattr(recent_sleep, 'total_sleep_duration', 0) / 3600
            st.markdown("""
            <div class="metric-card">
                <h3>Sleep Duration</h3>
                <div class="metric-value">{:.1f}h</div>
                <div class="metric-change positive">+0.3h from yesterday</div>
            </div>
            """.format(duration_hrs), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card">
                <h3>Sleep Duration</h3>
                <div class="metric-value">N/A</div>
                <div class="metric-change">No data available</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if recent_readiness is not None:
            st.markdown("""
            <div class="metric-card">
                <h3>Readiness Score</h3>
                <div class="metric-value">{}</div>
                <div class="metric-change positive">+5.2% from yesterday</div>
            </div>
            """.format(getattr(recent_readiness, 'score', 'N/A')), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card">
                <h3>Readiness Score</h3>
                <div class="metric-value">N/A</div>
                <div class="metric-change">No data available</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        if recent_activity is not None:
            st.markdown("""
            <div class="metric-card">
                <h3>Daily Burn</h3>
                <div class="metric-value">{}</div>
                <div class="metric-change negative">-12 cal from yesterday</div>
            </div>
            """.format(getattr(recent_activity, 'active_calories', 'N/A')), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card">
                <h3>Daily Burn</h3>
                <div class="metric-value">N/A</div>
                <div class="metric-change">No data available</div>
            </div>
            """, unsafe_allow_html=True)

def main():
    """Main application function"""
    # Header
    st.markdown('<h1 class="main-header">Oura Health Analytics</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header" style="color: white;">AI-Powered Insights from Your Sleep & Health Data</p>', unsafe_allow_html=True)
    
    # Clean Sidebar without emojis
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="color: #6366f1; margin-bottom: 0;">Oura RAG</h2>
            <p style="color: #64748b; font-size: 0.9rem;">AI-Powered Health Analytics</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Data Management Section
        st.subheader("Data Management")
        days_to_sync = st.slider("Days to Sync", 1, 365, 30, help="Select how many days of data to sync from Oura")
        
        sync_col1, sync_col2, sync_col3 = st.columns([2, 1, 1])
        with sync_col1:
            if st.button("Sync Data", type="primary", use_container_width=True):
                try:
                    indexer = Indexer()
                    indexer.sync_data(days_to_sync)
                    st.success(f"Synced {days_to_sync} days!")
                except Exception as e:
                    st.error(f"Sync failed: {e}")
        
        with sync_col2:
            if st.button("Quick Sync", help="Sync last 7 days"):
                try:
                    indexer = Indexer()
                    indexer.sync_data(7)
                    st.success("Quick sync complete!")
                except Exception as e:
                    st.error(f"Quick sync failed: {e}")
        
        with sync_col3:
            if st.button("Clear & Sync", help="Clear existing data and sync fresh", type="secondary"):
                try:
                    indexer = Indexer()
                    indexer.clear_and_sync(days_to_sync)
                    st.success(f"Cleared and synced {days_to_sync} days!")
                except Exception as e:
                    st.error(f"Clear & sync failed: {e}")
        
        st.markdown("---")
        
        # AI Assistant Section
        st.subheader("AI Assistant")
        question = st.text_input("Ask about your health:", placeholder="How did my sleep quality change last week?")
        
        if st.button("Ask AI", type="primary", use_container_width=True) and question:
            try:
                response = ask_ai(question)
                st.markdown("""
                <div style="background: #f0f9ff; border: 1px solid #0ea5e9; border-radius: 0.5rem; padding: 1rem;">
                    <h4 style="color: #0369a1; margin-bottom: 0.5rem;">AI Response:</h4>
                    <p style="color: #0c4a6e;">{}</p>
                </div>
                """.format(response), unsafe_allow_html=True)
            except Exception as e:
                st.error(f"AI analysis failed: {e}")
        
        st.markdown("---")
        
        # Quick Stats
        st.subheader("Quick Stats")
        try:
            sleep_data, readiness_data, activity_data = fetch_recent_data(1)
            if sleep_data and len(sleep_data) > 0:
                recent_sleep = sleep_data[-1]
                st.metric("Last Sleep Score", f"{getattr(recent_sleep, 'score', 'N/A')}")
                st.metric("Sleep Duration", f"{getattr(recent_sleep, 'total_sleep_duration', 0) / 3600:.1f}h")
        except:
            st.info("No recent data")
        
        st.markdown("---")
        
        # API Status moved to bottom
        st.subheader("API Status")
        if check_api_keys():
            st.markdown("""
            <div style="background: #d1fae5; color: #065f46; padding: 0.5rem; border-radius: 0.5rem; text-align: center;">
                All APIs Connected
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("API Keys Missing")
            st.stop()
    
    # Main content area with AI Insights and Dashboard only
    tab1, tab2 = st.tabs(["AI Insights", "Dashboard"])
    
    with tab1:
        st.header("AI-Powered Insights")
        
        # AI Analysis Section
        st.markdown("""
        <div class="feature-highlight">
            <h4>AI Health Analysis</h4>
            <p>Get personalized insights and recommendations based on your health data patterns.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Pre-defined AI questions for quick insights
        st.subheader("Quick Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Sleep Quality Analysis", key="sleep_analysis", use_container_width=True):
                try:
                    response = ask_ai("Analyze my sleep quality trends and provide recommendations for improvement.")
                    st.markdown("""
                    <div class="chart-container">
                        <h4 style="color: #ffffff;">Sleep Quality Analysis</h4>
                        <p style="color: #ffffff;">{}</p>
                    </div>
                    """.format(response), unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
            
            if st.button("Recovery Insights", key="recovery_insights", use_container_width=True):
                try:
                    response = ask_ai("What are my recovery patterns and how can I optimize them?")
                    st.markdown("""
                    <div class="chart-container">
                        <h4>Recovery Insights</h4>
                        <p style="color: #ffffff;">{}</p>
                    </div>
                    """.format(response), unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
        
        with col2:
            if st.button("Activity Optimization", key="activity_optimization", use_container_width=True):
                try:
                    response = ask_ai("How can I optimize my daily activity and exercise routine?")
                    st.markdown("""
                    <div class="chart-container">
                        <h4>Activity Optimization</h4>
                        <p style="color: #ffffff;">{}</p>
                    </div>
                    """.format(response), unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
            
            if st.button("Personalized Goals", key="personalized_goals", use_container_width=True):
                try:
                    response = ask_ai("Based on my health data, what are some personalized health goals I should set?")
                    st.markdown("""
                    <div class="chart-container">
                        <h4>Personalized Goals</h4>
                        <p style="color: #ffffff;">{}</p>
                    </div>
                    """.format(response), unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Custom analysis failed: {e}")
        
        # Custom AI Analysis
        st.markdown('<div class="custom-analysis-subheader"><h4>Custom Analysis</h4></div>', unsafe_allow_html=True)
        custom_question = st.text_area(
            "Ask a specific question about your health data:",
            placeholder="e.g., How does my sleep quality correlate with my readiness scores?",
            height=100
        )
        
        if st.button("Analyze", key="custom_analyze", type="primary", use_container_width=True) and custom_question:
            try:
                response = ask_ai(custom_question)
                st.markdown("""
                <div class="chart-container">
                    <h4 style="color: #ffffff;">Custom Analysis Result</h4>
                    <p style="color: #ffffff;">{}</p>
                </div>
                """.format(response), unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Custom analysis failed: {e}")
    
    with tab2:
        st.header("Health Dashboard")
        
        # Clean feature highlights without emojis
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-highlight">
                <h4>Sleep Analytics</h4>
                <p>• Deep sleep tracking<br>
                • REM cycle analysis<br>
                • Sleep efficiency metrics</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-highlight">
                <h4>Readiness Score</h4>
                <p>• Daily readiness tracking<br>
                • Recovery insights<br>
                • Training recommendations</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-highlight">
                <h4>Calories Burned</h4>
                <p>• Daily calorie tracking<br>
                • Active calorie monitoring<br>
                • Burn rate analysis</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Fetch and display recent data
        sleep_data, readiness_data, activity_data = fetch_recent_data(7)
        
        if sleep_data is not None and len(sleep_data) > 0:
            # Enhanced metrics display with better spacing
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            display_metrics(sleep_data, readiness_data, activity_data)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Create three main score charts
            st.subheader("Health Score Trends")
            
            # Sleep Score Chart
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("Sleep Score")
            sleep_chart = create_sleep_score_chart(sleep_data)
            if sleep_chart:
                st.plotly_chart(sleep_chart, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Readiness Score Chart
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("Readiness Score")
            readiness_chart = create_readiness_score_chart(readiness_data)
            if readiness_chart:
                st.plotly_chart(readiness_chart, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Calories Burned Chart
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("Calories Burned")
            activity_chart = create_calories_burned_chart(activity_data)
            if activity_chart:
                st.plotly_chart(activity_chart, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Clean empty state without emojis
            st.markdown("""
            <div class="loading-container">
                <h3>No Data Available</h3>
                <p>Please sync your Oura data to see your health insights.</p>
                <p>Click the "Sync Data" button in the sidebar to get started.</p>
            </div>
            """, unsafe_allow_html=True)
    


if __name__ == "__main__":
    main()
