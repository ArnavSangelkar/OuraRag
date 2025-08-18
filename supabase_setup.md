# Supabase Setup for Oura RAG

## 1. Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up/Login with GitHub
3. Click "New Project"
4. Choose organization
5. Enter project details:
   - Name: `oura-rag`
   - Database Password: (generate strong password)
   - Region: Choose closest to you
6. Click "Create new project"

## 2. Database Schema

### Tables to Create:

#### `health_data` table
```sql
CREATE TABLE health_data (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  data_type TEXT NOT NULL, -- 'sleep', 'readiness', 'activity'
  day DATE NOT NULL,
  data JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_health_data_user_type ON health_data(user_id, data_type);
CREATE INDEX idx_health_data_day ON health_data(day);
CREATE INDEX idx_health_data_user_day ON health_data(user_id, day);
```

#### `vector_chunks` table
```sql
CREATE TABLE vector_chunks (
  id TEXT PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  content TEXT NOT NULL,
  metadata JSONB NOT NULL,
  embedding VECTOR(1536), -- OpenAI embedding dimension
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
```

#### `user_settings` table
```sql
CREATE TABLE user_settings (
  user_id UUID REFERENCES auth.users(id) PRIMARY KEY,
  oura_token TEXT,
  openai_key TEXT,
  sync_days INTEGER DEFAULT 30,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 3. Row Level Security (RLS)

```sql
-- Enable RLS on all tables
ALTER TABLE health_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE vector_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;

-- Policies for health_data
CREATE POLICY "Users can view own health data" ON health_data
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own health data" ON health_data
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own health data" ON health_data
  FOR UPDATE USING (auth.uid() = user_id);

-- Policies for vector_chunks
CREATE POLICY "Users can view own vector chunks" ON vector_chunks
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own vector chunks" ON vector_chunks
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policies for user_settings
CREATE POLICY "Users can view own settings" ON user_settings
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own settings" ON user_settings
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own settings" ON user_settings
  FOR UPDATE USING (auth.uid() = user_id);
```

## 4. Environment Variables

Get these from your Supabase project settings:

- `SUPABASE_URL`: Your project URL
- `SUPABASE_ANON_KEY`: Your anon/public key
- `SUPABASE_SERVICE_ROLE_KEY`: Your service role key (keep secret)


