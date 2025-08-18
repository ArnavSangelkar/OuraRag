# 🚀 Render Deployment Checklist for Oura RAG + Supabase MCP

## ✅ Pre-Deployment Checklist

### 1. **Code Ready**
- [x] Supabase MCP integration complete
- [x] All tests passing (`python3 test_mcp.py` shows 4/4 tests passed)
- [x] Environment variables configured in `.env`
- [x] `render.yaml` configured
- [x] `requirements.txt` updated

### 2. **Supabase Setup**
- [x] Database tables created (`health_data`, `vector_chunks`, `user_settings`)
- [x] Row Level Security (RLS) policies configured
- [x] pgvector extension enabled
- [x] Service role key has proper permissions

### 3. **Git Repository**
- [x] All changes committed and pushed to GitHub
- [x] Repository is public or Render has access
- [x] Main branch contains latest code

## 🎯 Deployment Steps

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Add Supabase MCP integration and deployment config"
git push origin main
```

### Step 2: Deploy to Render

#### Option A: Automatic Deployment (Recommended)
1. **Connect GitHub to Render:**
   - Go to [render.com](https://render.com)
   - Sign in with GitHub
   - Click "New +" → "Web Service"
   - Connect your `oura-rag` repository

2. **Configure Service:**
   - **Name:** `oura-rag-app`
   - **Branch:** `main`
   - **Root Directory:** Leave empty (root)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command:** `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`

3. **Set Environment Variables:**
   ```
   SUPABASE_URL = your_supabase_project_url
   SUPABASE_ANON_KEY = your_supabase_anon_key  
   SUPABASE_SERVICE_ROLE_KEY = your_supabase_service_role_key
   OPENAI_API_KEY = your_openai_api_key
   OURA_PERSONAL_ACCESS_TOKEN = your_oura_token
   STREAMLIT_SERVER_HEADLESS = true
   STREAMLIT_SERVER_ENABLE_CORS = false
   STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION = false
   ```

4. **Create Service:**
   - Click "Create Web Service"
   - Wait for build (2-5 minutes)

#### Option B: Use render.yaml (Already Configured)
Your `render.yaml` is already set up correctly. Render will automatically:
- Use the specified build and start commands
- Set environment variables (you'll need to add the actual values)
- Configure health checks and auto-deploy

### Step 3: Verify Deployment

1. **Check Build Logs:**
   - Monitor the build process in Render dashboard
   - Ensure all dependencies install correctly
   - Verify no import errors

2. **Test Health Check:**
   - Your app should be available at `https://your-service-name.onrender.com`
   - Health check at `/` should return successfully

3. **Test MCP Functions:**
   - Navigate to your Streamlit app
   - Test the health data functions
   - Verify Supabase connection works

## 🔧 Post-Deployment Verification

### 1. **Test Core Functionality**
```bash
# Test your deployed app
curl https://your-service-name.onrender.com/
```

### 2. **Test MCP Integration**
- Open your Streamlit app in browser
- Try the health data functions
- Check if Supabase queries work

### 3. **Monitor Logs**
- Check Render dashboard for runtime logs
- Monitor for any errors or warnings
- Verify environment variables are loaded

## 🚨 Troubleshooting Common Issues

### Build Failures
```bash
# Check requirements.txt compatibility
pip install -r requirements.txt --dry-run

# Verify Python version compatibility
python --version
```

### Runtime Errors
```bash
# Check if MCP can connect locally first
python3 test_mcp.py

# Verify environment variables
echo $SUPABASE_URL
echo $SUPABASE_SERVICE_ROLE_KEY
```

### Database Connection Issues
- Verify Supabase service role key has proper permissions
- Check if database tables exist
- Ensure RLS policies are configured correctly

## 📊 Monitoring & Maintenance

### 1. **Health Monitoring**
- Render automatically monitors your service
- Failed health checks trigger restarts
- Monitor uptime in dashboard

### 2. **Performance**
- Free tier sleeps after 15 minutes of inactivity
- Consider upgrading to Starter plan ($7/month) for always-on service
- Monitor memory and CPU usage

### 3. **Updates**
- Push to `main` branch triggers automatic redeployment
- Monitor build logs for any issues
- Test locally before pushing

## 🎉 Success Indicators

Your deployment is successful when:
- ✅ App builds without errors
- ✅ Streamlit interface loads in browser
- ✅ Supabase MCP functions work
- ✅ Health checks pass
- ✅ No runtime errors in logs
- ✅ Environment variables loaded correctly

## 🔗 Useful Links

- **Render Dashboard:** [dashboard.render.com](https://dashboard.render.com)
- **Supabase Dashboard:** [supabase.com/dashboard](https://supabase.com/dashboard)
- **Your App:** `https://your-service-name.onrender.com`

---

**🚀 Ready to deploy? Follow the steps above and your Oura RAG + Supabase MCP will be live on Render!**
