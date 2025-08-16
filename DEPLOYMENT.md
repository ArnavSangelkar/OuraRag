# 🚀 Deployment Guide - Oura RAG on Render

This guide will walk you through deploying your Oura RAG application on Render, a modern cloud platform that offers free hosting for web applications.

## 📋 Prerequisites

Before deploying, ensure you have:
- ✅ GitHub repository with your code
- ✅ Oura Ring Personal Access Token
- ✅ OpenAI API Key
- ✅ Render account (free at [render.com](https://render.com))

## 🎯 Step-by-Step Deployment

### 1. Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with your GitHub account
3. Verify your email address

### 2. Create New Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub account if not already connected
3. Select your `OuraRag` repository
4. Choose the `main` branch

### 3. Configure Service Settings

Use these exact settings for optimal performance:

| Setting | Value |
|---------|-------|
| **Name** | `oura-rag-app` |
| **Environment** | `Python 3` |
| **Region** | `Oregon` (or your preferred region) |
| **Branch** | `main` |
| **Build Command** | `pip install --upgrade pip && pip install -r requirements.txt` |
| **Start Command** | `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true` |
| **Plan** | `Starter` (Free) |

### 4. Set Environment Variables

In your Render service dashboard, add these environment variables:

| Key | Value | Description |
|-----|-------|-------------|
| `OURA_PERSONAL_ACCESS_TOKEN` | `your_oura_token` | Get from [Oura Cloud](https://cloud.ouraring.com/personal-access-tokens) |
| `OPENAI_API_KEY` | `your_openai_key` | Get from [OpenAI Platform](https://platform.openai.com/api-keys) |
| `SUPABASE_URL` | `your_supabase_url` | Optional: Your Supabase project URL |
| `SUPABASE_ANON_KEY` | `your_supabase_anon_key` | Optional: Your Supabase anonymous key |
| `SUPABASE_SERVICE_ROLE_KEY` | `your_supabase_service_role_key` | Optional: Your Supabase service role key |

**Important:** Mark all API keys as **"Secret"** for security.

### 5. Deploy Your Service

1. Click **"Create Web Service"**
2. Wait for the build to complete (usually 2-5 minutes)
3. Your app will be available at: `https://your-service-name.onrender.com`

## 🔧 GitHub Actions Integration

Your repository already includes GitHub Actions for automatic deployment. To enable it:

### 1. Get Render Service ID

1. Go to your Render service dashboard
2. Copy the service ID from the URL: `https://dashboard.render.com/web/your-service-id`

### 2. Get Render API Key

1. Go to Render dashboard → **Account** → **API Keys**
2. Click **"Create API Key"**
3. Copy the generated key

### 3. Add GitHub Secrets

In your GitHub repository:
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:
   - `RENDER_SERVICE_ID`: Your service ID
   - `RENDER_API_KEY`: Your API key

### 4. Automatic Deployment

Now every push to `main` will automatically:
- ✅ Run tests
- ✅ Deploy to Render
- ✅ Update your live application

## 🌐 Custom Domain (Optional)

To use a custom domain:

1. **In Render:**
   - Go to your service → **Settings** → **Custom Domains**
   - Add your domain (e.g., `oura-rag.yourdomain.com`)

2. **In your DNS provider:**
   - Add CNAME record pointing to `your-service-name.onrender.com`

## 📊 Monitoring & Logs

### View Logs
- **Build Logs:** See during deployment
- **Runtime Logs:** Available in your service dashboard
- **Real-time Logs:** Click "Logs" tab in your service

### Health Checks
- Your app includes health check at `/`
- Render automatically monitors your service
- Failed health checks trigger automatic restarts

## 🚨 Troubleshooting

### Common Issues & Solutions

#### 1. Build Failures
```
Error: pip install failed
```
**Solution:**
- Check `requirements.txt` syntax
- Ensure all dependencies are available
- Verify Python version compatibility

#### 2. Runtime Errors
```
Error: Module not found
```
**Solution:**
- Verify all imports in your code
- Check `requirements.txt` includes all needed packages
- Ensure proper file structure

#### 3. Environment Variable Issues
```
Error: API key not found
```
**Solution:**
- Double-check environment variable names
- Ensure values are marked as "Secret"
- Verify no extra spaces in values

#### 4. Port Issues
```
Error: Port already in use
```
**Solution:**
- Use `$PORT` environment variable (already configured)
- Ensure Streamlit runs on `0.0.0.0` address

### Debug Commands

Add these to your `startCommand` for debugging:
```bash
streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true --logger.level debug
```

## ⚡ Performance Optimization

### 1. Enable Caching
Your app includes Streamlit caching for better performance:
```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_data():
    # Your data fetching logic
```

### 2. Optimize Dependencies
- Remove unused packages from `requirements.txt`
- Use specific versions for stability
- Consider using `pip-tools` for dependency management

### 3. Database Optimization
- Use connection pooling for database connections
- Implement proper indexing for vector searches
- Consider Redis for session storage

## 🔒 Security Best Practices

### 1. Environment Variables
- ✅ Never commit API keys to Git
- ✅ Use Render's secret management
- ✅ Rotate keys regularly

### 2. API Security
- ✅ Implement rate limiting
- ✅ Add authentication if needed
- ✅ Validate all inputs

### 3. HTTPS
- ✅ Render provides free SSL certificates
- ✅ Force HTTPS redirects
- ✅ Use secure cookies

## 📈 Scaling Considerations

### Free Tier Limitations
- **Build Time:** 15 minutes max
- **Runtime:** Sleeps after 15 minutes of inactivity
- **Bandwidth:** 100 GB/month
- **Storage:** 1 GB

### Upgrade Path
When you need more resources:
1. **Starter Plan:** $7/month
   - Always-on service
   - 512 MB RAM
   - Shared CPU
2. **Standard Plan:** $25/month
   - 1 GB RAM
   - Dedicated CPU
   - Custom domains

## 🎉 Success Checklist

Before considering deployment complete:

- ✅ Application builds successfully
- ✅ Environment variables are set
- ✅ Health checks pass
- ✅ API endpoints respond
- ✅ Streamlit interface loads
- ✅ Data sync works
- ✅ AI chat functions
- ✅ GitHub Actions deploy automatically

## 🆘 Getting Help

### Render Support
- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com)
- [Render Status](https://status.render.com)

### Application Issues
- Check [GitHub Issues](https://github.com/ArnavSangelkar/OuraRag/issues)
- Review application logs
- Test locally first

### Performance Issues
- Monitor Render metrics
- Check application performance
- Optimize database queries

---

**🎯 Your Oura RAG app is now ready for production deployment!**

For additional help, check the [README.md](README.md) or create an issue in the repository.

