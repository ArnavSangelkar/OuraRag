# Use Python 3.11.18 specifically
FROM python:3.11.18-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Show Python version for debugging
RUN python --version && pip --version

# Copy requirements first for better caching
COPY ../requirements.txt.bak requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir numpy==1.23.5 && \
    pip install --no-cache-dir pandas==1.5.3 && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY .. .

# Expose port
EXPOSE $PORT

# Set environment variables
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Run the application
CMD streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
