@echo off
REM Check if Ollama is installed
where ollama >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo X Ollama is not installed. Please install it from https://ollama.ai/download
    exit /b 1
)

REM Check if Ollama is already running
curl -s "http://localhost:11434/api/health" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ Ollama is already running
) else (
    echo Starting Ollama service...
    start /B ollama serve
    
    REM Wait for Ollama to start
    set MAX_RETRIES=10
    set RETRY=0
    :RETRY_LOOP
    timeout /t 1 >nul
    curl -s "http://localhost:11434/api/health" >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        set /a RETRY+=1
        if %RETRY% LSS %MAX_RETRIES% goto RETRY_LOOP
        echo X Failed to start Ollama service
        exit /b 1
    )
    echo ✓ Ollama service started
)

REM Check if llava model is available
ollama list | findstr "llava" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ LLaVA model is already available
) else (
    echo Pulling LLaVA model (this may take some time)...
    ollama pull llava
)

REM Start LLaVA in the background
echo Starting LLaVA model...
start /B ollama run llava

REM Start Streamlit app
echo Starting Streamlit app...
streamlit run app.py 