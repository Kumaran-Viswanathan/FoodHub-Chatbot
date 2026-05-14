FROM python:3.10-slim

# Install system dependencies with retries to handle transient network issues
RUN apt-get update || (sleep 5 && apt-get update) && apt-get install -y \
    build-essential \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create user
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy requirements first for better caching
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY --chown=user:user . .

# HF Spaces expects the app on port 7860 by default
EXPOSE 7860

# Combined command: Start backend in background, then Streamlit on port 7860
CMD uvicorn backend:app --host 0.0.0.0 --port 8000 & \
    streamlit run app.py --server.port 7860 --server.address 0.0.0.0
