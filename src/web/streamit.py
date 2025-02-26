# src/web/app.py

##############################################
# 1) Monkey-Patch Streamlit Watcher (Important)
##############################################
"""
Disables Streamlit's file-watching mechanism, which causes
errors when scanning PyTorch's 'torch.classes'.
"""
try:
    import streamlit.web.cli as stcli
    from streamlit.watcher import local_sources_watcher
    # Override the register_watcher method with a no-op
    # local_sources_watcher._file_watcher._register_watcher = lambda *args, **kwargs: None
except ImportError:
    pass

################################################
# 2) Now Import Streamlit and Other Dependencies
################################################
import streamlit as st
import os
import sys
import base64
from io import BytesIO
from pathlib import Path

# Optionally suppress PyTorch warnings
import warnings
import torch
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    # Attempt to set torch.classes._path to avoid reflection calls
    if not hasattr(torch, 'classes') or not hasattr(torch.classes, '_path'):
        torch.classes._path = []

# Add the project root to Python path using pathlib for better path handling
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

###############################################
# 3) Import Your Local Modules (After Patching)
###############################################
try:
    from src.llm.llm_processor import LLMProcessor
    from src.scoring.wcag_scorer import WCAGScorer
except ImportError as e:
    st.error(f"Failed to import required modules: {e}")
    st.stop()

###############################################
# 4) Streamlit Page Config
###############################################
st.set_page_config(
    page_title="PPT Accessibility Analyzer & Fixer (WCAG 2.1)", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.example.com/help',
        'Report a bug': "https://www.example.com/bug",
        'About': "PowerPoint Accessibility Analyzer v1.0"
    }
)

################################################
# 5) Path to Static Directory
################################################
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
print('STATIC_DIR', STATIC_DIR)

################################################
# 6) Initialize Session State for LLM and Scorer
################################################
if 'processors_initialized' not in st.session_state:
    st.session_state.llm_processor = LLMProcessor()
    st.session_state.wcag_scorer = WCAGScorer(st.session_state.llm_processor)
    st.session_state.processors_initialized = True

###############################################
# 7) Utility: Convert Images to Base64
###############################################
def load_image_as_base64(image_path):
    """Load an image file and convert it to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

###############################################
# 8) Attempt to Load Images (Fallback if Fails)
###############################################
try:
    wcag_logo = load_image_as_base64(os.path.join(STATIC_DIR, "images", "wcag-logo.png"))
    upload_icon = load_image_as_base64(os.path.join(STATIC_DIR, "images", "upload-icon.png"))
    hero_image = load_image_as_base64(os.path.join(STATIC_DIR, "images", "accessibility-hero.jpg"))
except Exception as e:
    print(f"Error loading images: {e}")
    # Fallback SVG icons if images fail to load
    wcag_logo = """
    <svg width="200" height="200" viewBox="0 0 200 200">
        <rect width="200" height="200" fill="#4CAF50"/>
        <text x="50%" y="50%" fill="white" font-size="24" text-anchor="middle">WCAG 2.1</text>
    </svg>
    """
    upload_icon = """
    <svg width="50" height="50" viewBox="0 0 24 24" fill="none" stroke="#4CAF50" stroke-width="2">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
        <polyline points="17 8 12 3 7 8"/>
        <line x1="12" y1="3" x2="12" y2="15"/>
    </svg>
    """
    hero_image = ""

###############################################
# 9) Inject Custom CSS / Styling
###############################################
st.markdown("""
    <style>
    /* Modern clean background */
    .stApp {
        background-color: white;
    }
    
    /* Modern container styling */
    .main {
        padding: 2rem;
        background-color: white;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Modern progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #4CAF50, #45a049);
        transition: all 0.3s ease;
    }
    
    /* Modern card styling */
    .modern-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 15px 0;
        transition: all 0.3s ease;
        border: 1px solid rgba(0,0,0,0.05);
        position: relative;
        overflow: hidden;
    }
    
    .modern-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: translateX(-100%);
        transition: 0.5s;
    }
    
    .modern-card:hover::before {
        transform: translateX(100%);
    }
    
    /* Modern button styling */
    .stButton>button {
        width: 100%;
        padding: 0.6em 2em;
        border-radius: 8px;
        background: linear-gradient(90deg, #4CAF50, #45a049);
        color: white;
        border: none;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(76,175,80,0.2);
    }
    
    /* Modern feature box */
    .feature-box {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        border-radius: 12px;
        padding: 25px;
        margin: 15px 0;
        border: 1px solid #f0f0f0;
        transition: transform 0.2s ease;
    }
    
    .feature-box:hover {
        transform: translateY(-2px);
    }
    
    /* Modern metric card */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
        transition: transform 0.2s ease;
        border: 1px solid #f0f0f0;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
    }
    
    /* Modern issue item */
    .issue-item {
        background: white;
        padding: 15px;
        border-radius: 8px;
        margin: 8px 0;
        border: 1px solid #f0f0f0;
        transition: transform 0.2s ease;
    }
    
    .issue-item:hover {
        transform: translateX(5px);
    }
    
    /* Modern headings */
    h1, h2, h3, h4 {
        color: #1a1a1a;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    /* Modern file uploader */
    .uploadedFile {
        border-radius: 12px;
        border: 2px dashed #4CAF50;
        padding: 20px;
        text-align: center;
    }
    
    /* Animations */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    @keyframes slideIn {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes fadeInUp {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    /* Animated elements */
    .float-animation {
        animation: float 3s ease-in-out infinite;
    }
    
    .slide-in {
        animation: slideIn 0.6s ease-out forwards;
    }
    
    .fade-in-up {
        animation: fadeInUp 0.8s ease-out forwards;
    }
    
    .pulse-animation {
        animation: pulse 2s infinite;
    }
    
    /* Modern sidebar */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Enhanced upload area */
    .upload-area {
        border: 2px dashed #4CAF50;
        border-radius: 15px;
        padding: 40px;
        text-align: center;
        transition: all 0.3s ease;
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
    }
    
    .upload-area:hover {
        border-color: #45a049;
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    /* Glowing effect for important elements */
    .glow-effect {
        position: relative;
    }
    
    .glow-effect::after {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        border-radius: 16px;
        background: linear-gradient(45deg, #4CAF50, #45a049, #4CAF50);
        z-index: -1;
        opacity: 0;
        transition: 0.3s;
    }
    
    .glow-effect:hover::after {
        opacity: 1;
    }
    
    /* Progress animation */
    @keyframes progressFill {
        from { width: 0; }
        to { width: var(--target-width); }
    }
    
    .animated-progress {
        animation: progressFill 1s ease-out forwards;
    }
    
    /* Score comparison styling */
    .score-comparison {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 20px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 20px 0;
    }

    .score-card {
        text-align: center;
        padding: 20px;
        flex: 1;
        position: relative;
    }

    .score-card:first-child::after {
        content: '→';
        position: absolute;
        right: -10px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 2em;
        color: #4CAF50;
        animation: arrowPulse 1.5s infinite;
    }

    @keyframes arrowPulse {
        0% { transform: translateY(-50%) scale(1); }
        50% { transform: translateY(-50%) scale(1.2); }
        100% { transform: translateY(-50%) scale(1); }
    }

    .score-value {
        font-size: 3em;
        font-weight: bold;
        margin: 10px 0;
        animation: countUp 2s ease-out forwards;
    }

    @keyframes countUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .score-label {
        color: #666;
        font-size: 0.9em;
        margin-bottom: 5px;
    }

    .improvement-badge {
        background: #4CAF50;
        color: white;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.8em;
        margin-top: 10px;
        display: inline-block;
        animation: fadeInUp 0.5s ease-out forwards;
    }
    
    /* Error message styling */
    .error-message {
        background-color: #ffebee;
        color: #c62828;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #c62828;
        margin: 1rem 0;
    }

    .warning-message {
        background-color: #fff3e0;
        color: #ef6c00;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ef6c00;
        margin: 1rem 0;
    }
    
    </style>
""", unsafe_allow_html=True)

###############################################
# 10) Sidebar Layout
###############################################
with st.sidebar:
    st.markdown(f"""
        <div class='modern-card slide-in'>
            <img src="data:image/png;base64,{wcag_logo}" alt="WCAG Logo" 
                 style="width: 200px; margin-bottom: 20px;" class="float-animation">
            <h4 style='color: #2E7D32; margin-top: 0;'>🚀 Welcome!</h4>
            <p style='font-size: 0.95em; color: #666;'>
                Transform your presentations with our AI-powered accessibility analyzer.
            </p>
            <div style='margin-top: 15px; padding-top: 15px; border-top: 1px solid #f0f0f0;'>
                <small style='color: #888;'>Version 1.0.0</small>
            </div>
        </div>
    """, unsafe_allow_html=True)

###############################################
# 11) Main Header / Hero
###############################################
st.markdown("""
    <div class='fade-in-up'>
        <h1 style='color: #2E7D32; font-size: 2.5em; margin-bottom: 30px;'>
            🎯 PowerPoint Accessibility Analyzer
        </h1>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class='feature-box fade-in-up' style='animation-delay: 0.2s;'>
        <h3 style='color: #2E7D32; margin-top: 0;'>Transform Your Presentations</h3>
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 25px;'>
            <div class='modern-card pulse-animation' style='animation-delay: 0.3s;'>
                🎯 Smart Title Detection
            </div>
            <div class='modern-card pulse-animation' style='animation-delay: 0.4s;'>
                🖼️ AI Alt Text Generation
            </div>
            <div class='modern-card pulse-animation' style='animation-delay: 0.5s;'>
                📊 Table Structure Analysis
            </div>
            <div class='modern-card pulse-animation' style='animation-delay: 0.6s;'>
                📝 Content Enhancement
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

###############################################
# 12) File Uploader & Analysis Logic
###############################################
upload_container = st.container()

with upload_container:
    st.markdown("""
        <div style='padding: 20px 0;'>
            <h3 style='color: #2E7D32; margin-bottom: 20px;'>Upload Your Presentation</h3>
        </div>
    """, unsafe_allow_html=True)
    
    try:
        uploaded_file = st.file_uploader(
            "Choose a PowerPoint file",
            type=["pptx"],
            key="pptx_uploader",
            help="Upload a PowerPoint file (.pptx) to analyze its accessibility",
            accept_multiple_files=False
        )

        if not uploaded_file:
            st.markdown(f"""
                <div class='upload-area'>
                    <div style='margin-bottom: 20px;'>
                        <img src="data:image/png;base64,{upload_icon}" alt="Upload Icon" 
                             style="width: 50px; height: 50px;">
                    </div>
                    <h3 style='color: #4CAF50; margin-bottom: 15px;'>Drop your PowerPoint file here</h3>
                    <p style='color: #666;'>or click to browse</p>
                    <p style='color: #888; font-size: 0.8em; margin-top: 10px;'>
                        Supported format: .pptx (max size: 200MB)
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            # Add file size warning
            st.markdown("""
                <div class='warning-message'>
                    <strong>📝 Note:</strong> For optimal performance, please ensure your presentation file is under 200MB.
                    Larger files may take longer to process.
                </div>
            """, unsafe_allow_html=True)

        if uploaded_file is not None:
            # Validate file size (200MB limit)
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # Size in MB
            
            if file_size > 200:
                st.markdown("""
                    <div class='error-message'>
                        <strong>❌ Error:</strong> File size exceeds 200MB limit. Please upload a smaller file.
                    </div>
                """, unsafe_allow_html=True)
            else:
                # Show a loading state while processing
                with st.spinner("🔍 Analyzing your presentation..."):
                    try:
                        # Use the scorers from session state
                        presentation, score, issues = st.session_state.wcag_scorer.analyze_presentation(uploaded_file)

                        # Score comparison display
                        st.markdown("""
                            <div class='score-comparison fade-in-up'>
                                <div class='score-card'>
                                    <div class='score-label'>Accessibility Score</div>
                                    <div class='score-value' style='color: #4CAF50;'>{}/100</div>
                                </div>
                            </div>
                        """.format(score), unsafe_allow_html=True)
                        
                        # Progress visualization
                        st.markdown("### Accessibility Score")
                        st.progress(score/100)
                        
                        # Display issues
                        if issues:
                            with st.expander("📋 Detailed Analysis", expanded=True):
                                for issue in issues:
                                    st.markdown(f"""
                                        <div class='issue-item'>
                                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                                <strong>{issue}</strong>
                                            </div>
                                        </div>
                                    """, unsafe_allow_html=True)
                        else:
                            st.success("No accessibility issues found!")

                        # Save and offer download
                        output = BytesIO()
                        presentation.save(output)
                        output.seek(0)
                        
                        st.download_button(
                            label="⬇️ Download Analyzed Presentation",
                            data=output,
                            file_name="analyzed_presentation.pptx",
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                        )
                    except Exception as e:
                        st.markdown(f"""
                            <div class='error-message'>
                                <strong>❌ Error:</strong> An error occurred while processing your file. 
                                Please try again or contact support if the issue persists.
                                <br><small>Error details: {str(e)}</small>
                            </div>
                        """, unsafe_allow_html=True)
                        
    except Exception as e:
        st.markdown(f"""
            <div class='error-message'>
                <strong>❌ Error:</strong> An error occurred during file upload. 
                Please try again or contact support if the issue persists.
                <br><small>Error details: {str(e)}</small>
            </div>
        """, unsafe_allow_html=True)
