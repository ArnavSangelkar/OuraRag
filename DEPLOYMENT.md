# 🚀 Deployment Guide: Oura RAG with Supabase, GitHub, and Render

## 📋 **Prerequisites**

- GitHub account
- Supabase account
- Render account
- Oura Ring API token
- OpenAI API key

## 🔧 **Step 1: Set Up Supabase**

### 1.1 Create Supabase Project
1. Go to [https://supabase.com](https://supabase.com)
2. Sign up/Login with GitHub
3. Click "New Project"
4. Choose organization
5. Enter project details:
   - Name: `oura-rag`
   - Database Password: (generate strong password)
   - Region: Choose closest to you
6. Click "Create new project"

### 1.2 Set Up Database Schema
1. Go to SQL Editor in your Supabase dashboard
2. Run the SQL commands from `supabase_setup.md`
3. Enable pgvector extension
4. Set up Row Level Security (RLS)

### 1.3 Get API Keys
1. Go to Settings → API
2. Copy:
   - Project URL
   - Anon public key
   - Service role key (keep secret)

## 🔧 **Step 2: Set Up GitHub Repository**

### 2.1 Create Repository
1. Go to GitHub and create a new repository
2. Name it `oura-rag`
3. Make it public or private (your choice)

### 2.2 Push Your Code
```bash
git init
git add .
git commit -m "Initial commit: Oura RAG system"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/oura-rag.git
git push -u origin main
```

### 2.3 Set Up GitHub Secrets
1. Go to your repository → Settings → Secrets and variables → Actions
2. Add these secrets:
   - `RENDER_SERVICE_ID`: (you'll get this from Render)
   - `RENDER_API_KEY`: (you'll get this from Render)

## 🔧 **Step 3: Deploy to Render**

### 3.1 Create Render Account
1. Go to [https://render.com](https://render.com)
2. Sign up with GitHub
3. Connect your GitHub account

### 3.2 Deploy Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure the service:
   - Name: `oura-rag-app`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0`
   - Plan: Free (or paid for better performance)

### 3.3 Set Environment Variables
In your Render service settings, add these environment variables:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Your Supabase anon key
- `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service role key
- `OPENAI_API_KEY`: Your OpenAI API key
- `OURA_PERSONAL_ACCESS_TOKEN`: Your Oura token

### 3.4 Get Service ID and API Key
1. Go to your Render service settings
2. Copy the Service ID
3. Go to Account Settings → API Keys
4. Create a new API key
5. Add these to GitHub secrets

## 🔧 **Step 4: Update Streamlit App for Supabase**

### 4.1 Install Supabase Dependencies
```bash
pip install supabase pgvector
```

### 4.2 Update Environment Variables
Add to your `.env` file:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

## 🔧 **Step 5: Test Deployment**

### 5.1 Local Testing
```bash
# Test Supabase connection
python -c "
from app.supabase_client import SupabaseClient
client = SupabaseClient()
print('✅ Supabase connection successful')
"

# Test MCP
python supabase_mcp.py
```

### 5.2 Deploy and Test
1. Push changes to GitHub
2. Check GitHub Actions for deployment status
3. Visit your Render URL to test the app

## 🔧 **Step 6: Set Up Authentication (Optional)**

### 6.1 Enable Supabase Auth
1. Go to Authentication → Settings in Supabase
2. Enable email/password authentication
3. Configure OAuth providers if needed

### 6.2 Update Streamlit App
Add authentication to your Streamlit app using Supabase auth.

## 🔧 **Step 7: Monitor and Maintain**

### 7.1 Set Up Monitoring
- Enable Render logs
- Set up Supabase monitoring
- Configure alerts

### 7.2 Regular Maintenance
- Update dependencies
- Monitor API usage
- Backup database

## 🎯 **Benefits of This Setup**

### **Supabase Benefits:**
- ✅ **Real-time database** with PostgreSQL
- ✅ **Built-in authentication** and Row Level Security
- ✅ **Vector search** with pgvector
- ✅ **Automatic backups** and scaling
- ✅ **Real-time subscriptions**

### **GitHub Benefits:**
- ✅ **Version control** and collaboration
- ✅ **CI/CD** with GitHub Actions
- ✅ **Issue tracking** and project management
- ✅ **Code review** and pull requests

### **Render Benefits:**
- ✅ **Automatic deployments** from GitHub
- ✅ **SSL certificates** and CDN
- ✅ **Environment variables** management
- ✅ **Logs and monitoring**
- ✅ **Free tier** available

## 🚀 **Next Steps**

1. **Set up monitoring** and alerts
2. **Add more features** like data export
3. **Implement caching** for better performance
4. **Add user management** and sharing
5. **Create mobile app** using React Native

## 📞 **Support**

- Supabase: [Discord](https://discord.supabase.com)
- Render: [Documentation](https://render.com/docs)
- GitHub: [Community](https://github.com/community)

Your Oura RAG system is now production-ready with enterprise-grade infrastructure! 🎉

