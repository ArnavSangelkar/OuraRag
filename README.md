# Oura RAG - Sleep Data Analysis with AI

A powerful Retrieval-Augmented Generation (RAG) application that allows you to ask natural language questions about your Oura Ring sleep and health data. Get insights about your sleep patterns, HRV trends, recovery scores, and more through intelligent AI-powered analysis.

## 🚀 Features

- **Smart Data Retrieval**: Automatically syncs and indexes your Oura Ring data
- **Natural Language Queries**: Ask questions like "How did my sleep quality change last week?" or "What's my average HRV trend?"
- **AI-Powered Analysis**: Uses OpenAI's GPT-4 and embedding models for intelligent responses
- **Multiple Interfaces**: CLI, API, and Streamlit web app
- **Persistent Storage**: Local Chroma vector database for fast retrieval
- **Automatic Deployment**: GitHub Actions workflow for seamless deployment to Render

## 🏗️ Architecture

- **Backend**: FastAPI with async processing
- **Vector Database**: Chroma for semantic search
- **AI Models**: OpenAI text-embedding-3-large + GPT-4o-mini
- **Data Source**: Oura Ring API integration
- **Frontend**: Streamlit web interface
- **Deployment**: Render cloud hosting

## 📋 Prerequisites

- Python 3.8+
- Oura Ring account with Personal Access Token
- OpenAI API key
- Git

## 🛠️ Installation & Setup

### 1. Clone and Setup Environment

```bash
git clone https://github.com/ArnavSangelkar/OuraRag.git
cd oura-rag

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env and set your API keys:
# OURA_PERSONAL_ACCESS_TOKEN=...  # Get from https://cloud.ouraring.com/personal-access-tokens
# OPENAI_API_KEY=...              # Get from https://platform.openai.com/api-keys
```

### 3. Initial Data Sync

```bash
# Sync last 120 days of data and index into vector database
./sync.sh 120

# Or sync custom date range
./sync.sh 30  # Last 30 days
```

## 🚀 Usage

### Command Line Interface

Ask questions directly from the terminal:

```bash
./ask.sh "How did my average HRV trend in the last month?"
./ask.sh "What was my best sleep score this week?"
./ask.sh "Show me my recovery patterns"
```

### API Server

Run the FastAPI server for programmatic access:

```bash
./run_api.sh
```

The API will be available at `http://localhost:8000`

**Example API Usage:**
```bash
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is my average sleep duration?"}'
```

### Web Interface

Launch the Streamlit web app:

```bash
./run_streamlit.sh
```

Access the web interface at `http://localhost:8501`

## 🔧 Configuration

### Model Settings

You can customize the AI models used in `app/vectorstore.py` and `app/cli.py`:

- **Embeddings**: `text-embedding-3-large` (default)
- **Chat**: `gpt-4o-mini` (default)

### Data Storage

- Vector database persists under `vectorstore/`
- Data is automatically deduplicated by Oura ID
- Re-run sync anytime to get latest data

## 📊 Data Sources

The application indexes the following Oura Ring data:
- Sleep sessions and quality metrics
- Heart Rate Variability (HRV)
- Recovery scores
- Activity data
- Readiness scores
- Sleep stages and timing

## 🚀 Deployment

### Automatic Deployment (Recommended)

The repository includes GitHub Actions workflow (`.github/workflows/deploy.yml`) that automatically deploys to Render when you push to the main branch.

### Manual Deployment

1. Push your code to GitHub
2. Connect your repository to Render
3. Set environment variables in Render dashboard
4. Deploy!

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

If you encounter any issues:
1. Check the [Issues](https://github.com/ArnavSangelkar/OuraRag/issues) page
2. Review the [Deployment Guide](DEPLOYMENT.md)
3. Check [Supabase Setup](supabase_setup.md) for database configuration

## 🔗 Links

- [Oura Ring API Documentation](https://cloud.ouraring.com/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

**Built with ❤️ for better sleep insights**

