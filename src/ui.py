"""
UI components for the Streamlit application.
Handles display of UI elements and layouts.
"""

import streamlit as st
import os

def load_css():
    """Load custom CSS styles"""
    st.markdown("""
    <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        h1, h2, h3, h4 {
            color: #2E7D32;
        }
        
        .stButton>button {
            border-radius: 6px;
        }

        .stButton>button[data-baseweb="button"] {
            background-color: #4CAF50;
            color: white;
            font-weight: 600;
        }
        
        /* Score display styling */
        .score-display {
            text-align: center;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        /* Custom card styling */
        .card {
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        
        .card-green {
            background-color: #E8F5E9;
        }
        
        .card-blue {
            background-color: #E3F2FD;
        }
        
        .card-orange {
            background-color: #FFF3E0;
        }
        
        /* Button styling */
        .primary-button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border-radius: 4px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border: none;
        }
    </style>
    """, unsafe_allow_html=True)

def get_image_path(image_name):
    """Get the path to an image in the src/images directory"""
    return os.path.join("src", "images", image_name)

def display_header():
    """Display the application header with logo"""
    col1, col2 = st.columns([1, 3])

    # Check if the logo image exists and display it
    logo_path = get_image_path("accessibility_logo.png")
    if os.path.exists(logo_path):
        col1.image(logo_path, width=150)
    else:
        # Fallback icon if image doesn't exist
        col1.markdown("# 📊")

    col2.markdown("""
        <h1 style="color: #2E7D32; margin-bottom: 0;">PowerPoint Accessibility Enhancer</h1>
        <p style="font-size: 1.2em; color: #666;">Transform your presentations to be accessible for everyone</p>
    """, unsafe_allow_html=True)

def display_upload_section():
    """Display the file upload section"""
    st.markdown("""
        <h2 style="color: #2E7D32; margin-top: 40px;">Start by Uploading Your Presentation</h2>
    """, unsafe_allow_html=True)

    # Check if the upload icon exists
    upload_icon_path = get_image_path("upload_icon.png")
    if os.path.exists(upload_icon_path):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(upload_icon_path, width=80)

    # Return the uploaded file
    return st.file_uploader("Choose a PowerPoint file (.pptx)", type=["pptx"], label_visibility="collapsed")

def display_features_section():
    """Display the features section when no file is uploaded"""
    st.markdown("""
    <h3 style="color: #2E7D32; margin-top: 50px; margin-bottom: 30px;">Key Features</h3>
    """, unsafe_allow_html=True)
    
    feature_cols = st.columns(3)
    
    # Try to get feature images
    alt_text_img = get_image_path("alt_text_feature.png")
    contrast_img = get_image_path("contrast_feature.png")
    simplify_img = get_image_path("simplify_feature.png")
    
    # Feature 1: Alt Text
    with feature_cols[0]:
        if os.path.exists(alt_text_img):
            st.image(alt_text_img, use_column_width=True)
        st.markdown("""
        <div style="text-align: center; padding: 15px; background-color: white; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <h4 style="color: #1565C0; margin-top: 0;">Alt Text Generation</h4>
            <p style="color: #555;">AI-powered descriptions for images to improve screen reader compatibility</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Feature 2: Font & Contrast
    with feature_cols[1]:
        if os.path.exists(contrast_img):
            st.image(contrast_img, use_column_width=True)
        st.markdown("""
        <div style="text-align: center; padding: 15px; background-color: white; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <h4 style="color: #1565C0; margin-top: 0;">Font & Contrast Fixing</h4>
            <p style="color: #555;">Ensure text is readable with proper font sizes and contrast ratios</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Feature 3: Text Simplification
    with feature_cols[2]:
        if os.path.exists(simplify_img):
            st.image(simplify_img, use_column_width=True)
        st.markdown("""
        <div style="text-align: center; padding: 15px; background-color: white; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <h4 style="color: #1565C0; margin-top: 0;">Text Simplification</h4>
            <p style="color: #555;">Make complex text more readable for improved comprehension</p>
        </div>
        """, unsafe_allow_html=True)

def display_upload_placeholder():
    """Display a placeholder when no file is uploaded"""
    st.markdown("""
    <div style="border: 2px dashed #4CAF50; border-radius: 12px; padding: 30px; text-align: center; margin: 20px 0;">
        <h3 style="color: #2E7D32; margin-bottom: 15px;">Drag and drop your PowerPoint file here</h3>
        <p style="color: #666;">or click to browse files</p>
        <p style="color: #888; font-size: 0.8em; margin-top: 15px;">
            Supported format: .pptx
        </p>
    </div>
    """, unsafe_allow_html=True)

def display_analysis_results(before_score, wcag_report):
    """Display the analysis results"""
    st.markdown("<h3 style='color: #2E7D32;'>Analysis Results</h3>", unsafe_allow_html=True)
    
    # Display overall score
    score = before_score["overall_score"]
    
    # Progress bar with color based on score
    score_color = "#4CAF50" if score >= 80 else "#FFC107" if score >= 60 else "#F44336"
    
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h3 style="margin-bottom: 0.5rem;">Overall Accessibility Score</h3>
        <div style="font-size: 5rem; font-weight: 700; color: {score_color};">{score}</div>
        <p style="color: #555; margin-top: 0;">{before_score['summary']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display WCAG compliance chart
    from src.utils import create_wcag_compliance_chart
    compliance_chart = create_wcag_compliance_chart(wcag_report)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("<h3 style='color: #2E7D32;'>WCAG 2.1 Compliance</h3>", unsafe_allow_html=True)
        
        # Create a color-coded table for WCAG criteria with explicit black text
        for criteria, details in wcag_report.items():
            color = "#E8F5E9" if details["compliance"] == "Pass" else "#FFEBEE"
            border_color = "#43A047" if details["compliance"] == "Pass" else "#E53935"
            text_status = details["compliance"]
            
            st.markdown(
                f"""
                <div style="padding: 15px; background-color: {color}; border-left: 4px solid {border_color}; border-radius: 4px; margin-bottom: 10px; color: #000000;">
                    <strong style="color: #000000;">{criteria}</strong>: <span style="color: #000000;">{text_status}</span><br>
                    <small style="color: #000000;">{details["description"]}</small>
                </div>
                """, 
                unsafe_allow_html=True
            )
    
    with col2:
        st.markdown("<h3 style='color: #2E7D32;'>Compliance Summary</h3>", unsafe_allow_html=True)
        st.image(f"data:image/png;base64,{compliance_chart}", use_column_width=True)
    
    display_issues_section(wcag_report)

def display_issues_section(wcag_report):
    """Display the identified issues section"""
    st.markdown('<h3 style="color: #2E7D32;">Identified Issues</h3>', unsafe_allow_html=True)

    has_issues = False
    if wcag_report:
        # Define icons for each criteria type
        icons = {
            "1.1.1 Non-text Content": "🖼️",
            "1.4.3 Contrast": "👁️",
            "1.4.4 Resize Text": "🔍",
            "3.1.5 Reading Level": "📝"
        }
        
        # Define criteria colors for better visibility against white background
        criteria_colors = {
            "1.1.1 Non-text Content": "#1565C0",  # Deep blue
            "1.4.3 Contrast": "#6A1B9A",  # Purple
            "1.4.4 Resize Text": "#AD1457",  # Pink
            "3.1.5 Reading Level": "#2E7D32"   # Green
        }
        
        for criteria, details in wcag_report.items():
            if details["issues"]:
                has_issues = True
                icon = icons.get(criteria, "⚠️")
                
                # Get custom color for this criteria or fallback to dark gray
                criteria_color = criteria_colors.get(criteria, "#424242")
                
                # Determine compliance status color
                badge_color = "#4CAF50" if details["compliance"] == "Pass" else "#F44336"
                
                # Create better visible expander
                with st.expander(f"{icon} {criteria}"):
                    # Display status badge
                    st.markdown(f"""
                    <div style="display: inline-block; background-color: {badge_color}; color: white; 
                             padding: 3px 8px; border-radius: 12px; font-size: 0.8em; margin-bottom: 10px;">
                        {details["compliance"]}
                    </div>
                    """, unsafe_allow_html=True)
                        
                    # Display each issue with a bullet point
                    for issue in details["issues"]:
                        st.markdown(f"""
                        <div style="background-color: white; border-radius: 4px; padding: 10px; 
                                  margin-bottom: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); color: #000000;">
                            • {issue}
                        </div>
                        """, unsafe_allow_html=True)

        if not has_issues:
            st.success("✅ No accessibility issues found! Your presentation is already well-optimized.")

def display_enhancement_options():
    """Display the enhancement options section"""
    st.markdown("<h3 style='color: #2E7D32;'>Enhancement Options</h3>", unsafe_allow_html=True)
    
    # Use more visual enhancement options with descriptions
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background-color: white; border-radius: 8px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <h4 style="margin-top: 0; color: #1565C0;">Image Accessibility</h4>
            <p style="color: #555; font-size: 0.9rem;">Generate alternative text descriptions for images using LLaVA via Ollama to make them accessible to screen readers.</p>
        </div>
        """, unsafe_allow_html=True)
        generate_alt_text = st.checkbox("Generate Alt Text for Images", value=True)
        
        # Display warning if Ollama is not installed or running
        try:
            from src.alt_text_generator import AltTextGenerator
            generator = AltTextGenerator()
            if not generator.check_api_availability():
                if hasattr(generator, 'check_port_availability') and not generator.check_port_availability():
                    st.error("""
                        ⚠️ Port 11434 is in use by another application. 
                        Please close any other Ollama instances or applications using this port.
                    """)
                else:
                    st.warning("""
                        ⚠️ Ollama API not available. To use AI-generated alt text:
                        1. Install Ollama: https://ollama.ai/download
                        2. Run: `ollama serve` in one terminal
                        3. Run: `ollama run llava` in another terminal
                        4. Refresh this page
                        
                        Is Ollama installed? Check by typing 'ollama' in a terminal.
                    """)
        except Exception as e:
            st.error(f"⚠️ Ollama integration error: {str(e)}")
        
        # Add this to the enhancement options
        with st.expander("Advanced Options"):
            use_local_only = st.checkbox("Local-only mode (don't use Ollama)", 
                                        value=st.session_state.get('use_local_only', False))
            if use_local_only:
                st.info("Local-only mode enabled. Alt text will use basic placeholders instead of AI generation.")
            
            # Store in session state
            st.session_state['use_local_only'] = use_local_only
        
    return generate_alt_text

def display_enhance_button_and_process(generate_alt_text):
    """Display the enhance button and handle the enhancement process"""
    from src.enhancement import enhance_presentation_simple
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Clear previous state tracking variables
        if 'enhance_button_pressed' not in st.session_state:
            st.session_state.enhance_button_pressed = False
        
        # Simple button that sets a flag when pressed
        if st.button("🚀 Enhance Presentation", key="enhance_simple_btn", type="primary", use_container_width=True):
            st.session_state.enhance_button_pressed = True
        
        # The enhancement process runs when the flag is set
        if st.session_state.enhance_button_pressed:
            try:
                with st.spinner("⚙️ Enhancing presentation..."):
                    # Call enhancement function with explicit parameter list
                    after_score = enhance_presentation_simple(
                        st.session_state.ppt_processor, 
                        [generate_alt_text, True, True, True]
                    )
                    
                    # Check if after_score is not None before proceeding
                    if after_score is not None:
                        # Store results
                        st.session_state.after_score = after_score
                        st.session_state.enhanced_file_path = st.session_state.output_path
                        
                        # Display success and results
                        st.success("✅ Presentation successfully enhanced!")
                        
                        # Show improvement details
                        display_enhancement_results(after_score)
                    else:
                        st.error("Enhancement process failed to produce a valid score. Please try again.")
                    
            except Exception as e:
                st.error(f"Error enhancing presentation: {str(e)}")
                import traceback
                st.error(traceback.format_exc())

def display_enhancement_results(after_score):
    """Display the enhancement results with before and after comparison"""
    st.markdown("<h3 style='color: #2E7D32;'>Enhancement Results</h3>", unsafe_allow_html=True)
    
    # Create columns for before and after scores
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h4>Before Enhancement</h4>", unsafe_allow_html=True)
        before_score = st.session_state.before_score
        
        # Create a gauge chart for the before score
        before_fig = create_gauge_chart(
            before_score["overall_score"], 
            "Overall Accessibility Score", 
            color='#FFA726'
        )
        st.plotly_chart(before_fig, use_container_width=True)
        
        # Display category scores
        st.markdown("#### Category Scores")
        cat_scores = before_score["category_scores"]
        for cat, score in cat_scores.items():
            st.markdown(f"**{cat.replace('_', ' ').title()}:** {score}/100")
    
    with col2:
        st.markdown("<h4>After Enhancement</h4>", unsafe_allow_html=True)
        
        # Create a gauge chart for the after score
        after_fig = create_gauge_chart(
            after_score["overall_score"], 
            "Overall Accessibility Score", 
            color='#66BB6A'
        )
        st.plotly_chart(after_fig, use_container_width=True)
        
        # Display category scores
        st.markdown("#### Category Scores")
        cat_scores = after_score["category_scores"]
        for cat, score in cat_scores.items():
            # Calculate improvement and display with color
            before_cat_score = before_score["category_scores"][cat]
            improvement = score - before_cat_score
            if improvement > 0:
                st.markdown(f"**{cat.replace('_', ' ').title()}:** {score}/100 <span style='color:green'>(+{improvement})</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"**{cat.replace('_', ' ').title()}:** {score}/100")
    
    # Display overall improvement
    improvement = after_score["overall_score"] - before_score["overall_score"]
    if improvement > 0:
        st.success(f"Overall improvement: +{improvement} points")
    else:
        st.info("No significant score improvement detected.")
    
    # Download buttons
    col1, col2 = st.columns(2)
    
    with col1:
        with open(st.session_state.enhanced_file_path, "rb") as file:
            st.download_button(
                label="📥 Download Enhanced Presentation",
                data=file,
                file_name="enhanced_presentation.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                key="download_ppt_btn",
                use_container_width=True
            )
    
    with col2:
        st.download_button(
            label="📄 Download Accessibility Report",
            data=st.session_state.report_html,
            file_name="accessibility_report.html",
            mime="text/html",
            key="download_report_btn",
            use_container_width=True
        )
    
    # Reset button
    if st.button("Start Over", key="reset_btn"):
        st.session_state.enhance_button_pressed = False
        st.experimental_rerun()

def create_gauge_chart(score, title, color='#2E7D32'):
    """Create a gauge chart for the score"""
    import plotly.graph_objects as go
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 40], 'color': "lightgray"},
                {'range': [40, 70], 'color': "gray"},
                {'range': [70, 100], 'color': "lightgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='white',
    )
    
    return fig 