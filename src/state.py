"""
State management for the Streamlit application.
Handles session state initialization and management.
"""

import streamlit as st
import tempfile
import os

def initialize_session_state():
    """Initialize session state variables"""
    if 'before_score' not in st.session_state:
        st.session_state.before_score = None
    if 'after_score' not in st.session_state:
        st.session_state.after_score = None
    if 'enhanced_file_path' not in st.session_state:
        st.session_state.enhanced_file_path = None
    if 'report_html' not in st.session_state:
        st.session_state.report_html = None
    if 'temp_dir' not in st.session_state:
        st.session_state.temp_dir = None
    if 'input_path' not in st.session_state:
        st.session_state.input_path = None
    if 'output_path' not in st.session_state:
        st.session_state.output_path = None
    if 'analyzed' not in st.session_state:
        st.session_state.analyzed = False
    if 'ppt_processor' not in st.session_state:
        st.session_state.ppt_processor = None
    if 'wcag_report' not in st.session_state:
        st.session_state.wcag_report = None
    if 'enhance_button_pressed' not in st.session_state:
        st.session_state.enhance_button_pressed = False

def setup_file_paths(uploaded_file):
    """Setup temporary file paths for processing"""
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, "input.pptx")
    
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Store paths in session state
    st.session_state.temp_dir = temp_dir
    st.session_state.input_path = input_path
    st.session_state.output_path = os.path.join(temp_dir, "enhanced.pptx")
    
    return input_path, temp_dir 