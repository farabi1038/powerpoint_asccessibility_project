"""
PowerPoint Accessibility Enhancer

Streamlit web application for enhancing PowerPoint accessibility.
"""

import streamlit as st
import subprocess
import os
import sys
import time
from src.state import initialize_session_state
from src.ui import (
    load_css, display_header, display_upload_section, display_features_section,
    display_upload_placeholder, display_analysis_results, display_enhancement_options,
    display_enhance_button_and_process
)
from src.analysis import analyze_accessibility

# Set page configuration
st.set_page_config(
    page_title="PowerPoint Accessibility Enhancer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
load_css()

# Initialize session state
initialize_session_state()

# Display header
display_header()

# Check if Ollama is available - do this in a sidebar to not disrupt main UI
with st.sidebar:
    st.title("Ollama Status")
    
    try:
        import requests
        ollama_available = False
        
        try:
            response = requests.get("http://localhost:11434/api/health", timeout=1)
            if response.status_code == 200:
                st.success("✅ Ollama is running")
                ollama_available = True
            else:
                st.error("⚠️ Ollama is not responding properly")
        except:
            st.warning("⚠️ Ollama is not running")
            
            # Only show the start button if not already running
            if st.button("Start Ollama"):
                with st.spinner("Starting Ollama..."):
                    try:
                        # Check if ollama is installed
                        if sys.platform.startswith('win'):
                            check_installed = subprocess.run(["where", "ollama"], 
                                                         stdout=subprocess.PIPE, 
                                                         stderr=subprocess.PIPE)
                        else:
                            check_installed = subprocess.run(["which", "ollama"], 
                                                          stdout=subprocess.PIPE, 
                                                          stderr=subprocess.PIPE)
                        
                        if check_installed.returncode != 0:
                            st.error("Ollama is not installed. Please install it from https://ollama.ai/download")
                        else:
                            # Kill any existing ollama processes
                            if sys.platform.startswith('win'):
                                subprocess.run(["taskkill", "/f", "/im", "ollama.exe"], 
                                             stdout=subprocess.PIPE, 
                                             stderr=subprocess.PIPE)
                            else:
                                subprocess.run(["pkill", "-f", "ollama"], 
                                             stdout=subprocess.PIPE, 
                                             stderr=subprocess.PIPE)
                            
                            time.sleep(2)  # Give it time to shut down
                            
                            # Start Ollama with explicit path
                            if sys.platform.startswith('win'):
                                subprocess.Popen(["start", "cmd", "/c", "ollama", "serve"], 
                                               shell=True)
                            else:
                                subprocess.Popen(["ollama", "serve"], 
                                               stdout=subprocess.DEVNULL, 
                                               stderr=subprocess.DEVNULL)
                            
                            # Give Ollama time to start
                            time.sleep(5)
                            
                            # Now run the model
                            if sys.platform.startswith('win'):
                                subprocess.Popen(["start", "cmd", "/c", "ollama", "run", "llava"], 
                                               shell=True)
                            else:
                                subprocess.Popen(["ollama", "run", "llava"], 
                                               stdout=subprocess.DEVNULL, 
                                               stderr=subprocess.DEVNULL)
                            
                            # Wait a bit more
                            time.sleep(3)
                            
                            # Verify it's running
                            try:
                                response = requests.get("http://localhost:11434/api/health", timeout=5)
                                if response.status_code == 200:
                                    st.success("✅ Ollama started successfully!")
                                    ollama_available = True
                                else:
                                    st.error(f"Ollama started but returned an error: {response.status_code}")
                            except:
                                st.error("Ollama may have started but API is not responding")
                    except Exception as e:
                        st.error(f"Error starting Ollama: {str(e)}")
            
            st.markdown("""
            ### Manual Start
            
            If the automatic start doesn't work, please:
            
            1. Open a terminal/command prompt
            2. Run: `ollama serve`
            3. In another terminal, run: `ollama run llava`
            4. Refresh this page
            """)
        
        # Display model info if Ollama is available
        if ollama_available:
            try:
                models_response = requests.post("http://localhost:11434/api/tags", timeout=1)
                if models_response.status_code == 200:
                    models = models_response.json().get("models", [])
                    
                    # Check for LLaVA (for image description)
                    llava_models = [m for m in models if "llava" in m.get("name", "").lower()]
                    if llava_models:
                        st.success("✅ LLaVA model is available")
                        st.write(f"Using model: {llava_models[0]['name']}")
                    else:
                        st.warning("⚠️ LLaVA model is not available")
                        if st.button("Pull LLaVA Model"):
                            with st.spinner("Downloading LLaVA model..."):
                                os.system("ollama pull llava")
            except:
                st.warning("⚠️ Could not check available models")
    except ImportError:
        st.error("❌ Requests library is not installed. Alt text generation may not work properly.")

# Display upload section
uploaded_file = display_upload_section()

if not uploaded_file:
    display_upload_placeholder()
    display_features_section()
else:
    # Display analyze button if file is uploaded but not yet analyzed
    if not st.session_state.analyzed:
        if st.button("🔍 Analyze Accessibility", key="analyze_btn", type="primary", use_container_width=True):
            with st.spinner("Analyzing your presentation..."):
                before_score, wcag_report = analyze_accessibility(uploaded_file)
                st.session_state.analyzed = True
                
                # Display analysis results
                display_analysis_results(before_score, wcag_report)
                
                # Display enhancement options
                generate_alt_text, fix_font_size, improve_contrast, simplify_text = display_enhancement_options()
                
                # Handle enhancement
                display_enhance_button_and_process(generate_alt_text, fix_font_size, improve_contrast, simplify_text)
    
    # If already analyzed, show results
    elif st.session_state.analyzed:
        # Display analysis results
        display_analysis_results(st.session_state.before_score, st.session_state.wcag_report)
        
        # Display enhancement options
        generate_alt_text, fix_font_size, improve_contrast, simplify_text = display_enhancement_options()
        
        # Handle enhancement
        display_enhance_button_and_process(generate_alt_text, fix_font_size, improve_contrast, simplify_text)

# Show info message if needed
if not st.session_state.analyzed and not st.session_state.get('enhance_button_pressed', False):
    st.info("Analyze your presentation to see enhancement options.")
        