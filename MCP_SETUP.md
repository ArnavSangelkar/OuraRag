# Supabase MCP Setup Guide for Oura RAG

This guide will help you set up Supabase MCP (Model Context Protocol) integration with your Oura RAG system.

## Prerequisites

1. **Supabase Project**: You need a Supabase project set up (see `supabase_setup.md`)
2. **Environment Variables**: Configure your `.env` file
3. **Dependencies**: Install required packages

## Step 1: Environment Setup

Create or update your `.env` file with the following variables:

```bash
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# OpenAI Configuration (for embeddings)
OPENAI_API_KEY=your_openai_api_key

# Oura Configuration
OURA_PERSONAL_ACCESS_TOKEN=your_oura_token
```

## Step 2: Install Dependencies

The required dependencies are already in your `requirements.txt`. Install them:

```bash
pip install -r requirements.txt
```

## Step 3: Database Schema Setup

Run the following SQL commands in your Supabase SQL editor:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create health_data table
CREATE TABLE health_data (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  data_type TEXT NOT NULL, -- 'sleep', 'readiness', 'activity'
  day DATE NOT NULL,
  data JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create vector_chunks table
CREATE TABLE vector_chunks (
  id TEXT PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  content TEXT NOT NULL,
  metadata JSONB NOT NULL,
  embedding VECTOR(1536), -- OpenAI embedding dimension
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user_settings table
CREATE TABLE user_settings (
  user_id UUID REFERENCES auth.users(id) PRIMARY KEY,
  oura_token TEXT,
  openai_key TEXT,
  sync_days INTEGER DEFAULT 30,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_health_data_user_type ON health_data(user_id, data_type);
CREATE INDEX idx_health_data_day ON health_data(day);
CREATE INDEX idx_health_data_user_day ON health_data(user_id, day);
CREATE INDEX idx_vector_chunks_user ON vector_chunks(user_id);
CREATE INDEX idx_vector_chunks_embedding ON vector_chunks USING ivfflat (embedding vector_cosine_ops);

-- Enable Row Level Security
ALTER TABLE health_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE vector_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Users can view own health data" ON health_data
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own health data" ON health_data
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own health data" ON health_data
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own vector chunks" ON vector_chunks
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own vector chunks" ON vector_chunks
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own settings" ON user_settings
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own settings" ON user_settings
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own settings" ON user_settings
  FOR UPDATE USING (auth.uid() = user_id);
```

## Step 4: Test Supabase MCP

Create a test script to verify your setup:

```python
# test_mcp.py
import os
from dotenv import load_dotenv
from supabase_mcp import SupabaseMCP

load_dotenv()

def test_mcp_connection():
    try:
        mcp = SupabaseMCP()
        print("✅ Supabase MCP connection successful!")
        
        # Test with a sample user ID (replace with actual user ID)
        # user_id = "your-user-uuid"
        # summary = mcp.get_health_summary(user_id, days=7)
        # print("Health summary:", summary)
        
    except Exception as e:
        print(f"❌ MCP connection failed: {e}")

if __name__ == "__main__":
    test_mcp_connection()
```

Run the test:
```bash
python test_mcp.py
```

## Step 5: Integration with Your RAG System

The Supabase MCP is already integrated into your system. Here's how to use it:

### In your API (`app/api.py`):
```python
from supabase_mcp import SupabaseMCP

# Initialize MCP
mcp = SupabaseMCP()

# Get health summary
@app.get("/health/summary/{user_id}")
async def get_health_summary(user_id: str, days: int = 30):
    return mcp.get_health_summary(user_id, days)

# Get user insights
@app.get("/health/insights/{user_id}")
async def get_user_insights(user_id: str):
    return mcp.get_user_insights(user_id)
```

### In your Streamlit app (`streamlit_app.py`):
```python
from supabase_mcp import SupabaseMCP

# Initialize MCP
mcp = SupabaseMCP()

# Use in your Streamlit interface
if st.button("Get Health Summary"):
    summary = mcp.get_health_summary(user_id, days=30)
    st.json(summary)
```

## Step 6: Available MCP Functions

The Supabase MCP provides these main functions:

1. **`get_health_summary(user_id, days)`**: Get health data summary for a user
2. **`search_health_patterns(user_id, query, limit)`**: Search for health patterns
3. **`get_user_insights(user_id)`**: Generate personalized health insights
4. **`get_data_quality_report(user_id)`**: Check data quality and completeness

## Step 7: Security Considerations

1. **Service Role Key**: The MCP uses the service role key for full database access
2. **Row Level Security**: RLS policies ensure users can only access their own data
3. **Environment Variables**: Never commit your `.env` file to version control

## Step 8: Troubleshooting

### Common Issues:

1. **Connection Error**: Check your `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`
2. **Permission Error**: Ensure RLS policies are correctly set up
3. **Missing Extension**: Make sure `pgvector` extension is enabled

### Debug Commands:

```bash
# Test Supabase connection
python -c "from supabase import create_client; import os; client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY')); print('Connection successful')"

# Test MCP functions
python test_mcp.py
```

## Step 9: Production Deployment

For production deployment:

1. Set environment variables in your deployment platform
2. Ensure database migrations are run
3. Test all MCP functions with real user data
4. Monitor database performance and adjust indexes as needed

## Next Steps

1. **Vector Search**: Implement semantic search using embeddings
2. **Real-time Sync**: Set up webhooks for real-time data updates
3. **Analytics**: Add more sophisticated health analytics
4. **Caching**: Implement caching for frequently accessed data

Your Supabase MCP is now ready to use! The system will allow AI models to interact with your health data securely and efficiently.
