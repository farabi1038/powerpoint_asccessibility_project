#!/bin/bash
# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed. Please install it from https://ollama.ai/download"
    exit 1
fi

# Special handling for WSL
if grep -q Microsoft /proc/version; then
    echo "🔍 WSL detected - using special networking setup"
    # Get Windows host IP
    WINDOWS_HOST=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
    
    # Export Ollama host for WSL
    export OLLAMA_HOST="http://$WINDOWS_HOST:11434"
    echo "Using OLLAMA_HOST=$OLLAMA_HOST"
fi

# Check if Ollama is already running
if curl -s "http://localhost:11434/api/health" &> /dev/null; then
    echo "✅ Ollama is already running"
else
    echo "🚀 Starting Ollama service..."
    nohup ollama serve > ollama.log 2>&1 &
    OLLAMA_PID=$!
    
    # Wait for Ollama to start
    MAX_RETRIES=10
    RETRY=0
    while ! curl -s "http://localhost:11434/api/health" &> /dev/null; do
        sleep 1
        RETRY=$((RETRY+1))
        if [ $RETRY -ge $MAX_RETRIES ]; then
            echo "❌ Failed to start Ollama service"
            exit 1
        fi
    done
    echo "✅ Ollama service started"
fi

# Check if llava model is available
if ollama list | grep -q "llava"; then
    echo "✅ LLaVA model is already available"
else
    echo "🔄 Pulling LLaVA model (this may take some time)..."
    ollama pull llava
fi

# Start LLaVA in the background
echo "🧠 Starting LLaVA model..."
nohup ollama run llava > llava.log 2>&1 &
LLAVA_PID=$!

# Start Streamlit app
echo "🚀 Starting Streamlit app..."
streamlit run app.py

# When Streamlit exits, clean up
echo "Shutting down background services..."
kill $LLAVA_PID
kill $OLLAMA_PID 