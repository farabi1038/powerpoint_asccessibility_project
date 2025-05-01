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
    """Display accessibility analysis results"""
    
    if not before_score or not wcag_report:
        st.error("No analysis results available.")
        return
    
    # Display the overall score prominently
    score_color = "#4CAF50" if before_score["overall_score"] >= 80 else "#FF9800" if before_score["overall_score"] >= 60 else "#F44336"
    
    # Create accessibility score section with improved visuals
    st.markdown(
        f"""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
            <h2 style="margin-top: 0;">Accessibility Score: <span style="color: {score_color};">{before_score["overall_score"]}/100</span></h2>
            <p style="color: #555; margin-top: 0;">Your presentation has been analyzed for accessibility compliance.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Create columns for different scores
    col1, col2, col3, col4 = st.columns(4)
    
    # Display category scores
    with col1:
        display_category_score("Alt Text", before_score["category_scores"]["alt_text"])
        
    with col2:
        display_category_score("Font Size", before_score["category_scores"]["font_size"])
        
    with col3:
        display_category_score("Contrast", before_score["category_scores"]["contrast"])
        
    with col4:
        display_category_score("Text Complexity", before_score["category_scores"]["text_complexity"])
    
    # Show summary statistics from the WCAG report
    st.markdown("### Presentation Summary")
    
    if "summary" in wcag_report:
        summary = wcag_report["summary"]
        st.markdown(
            f"""
            <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px;">
                <div style="flex: 1; min-width: 200px; background-color: #f1f8e9; padding: 15px; border-radius: 8px;">
                    <h4 style="margin-top: 0; color: #2E7D32;">Slides</h4>
                    <p style="font-size: 20px; font-weight: bold;">{summary.get("total_slides", 0)}</p>
                </div>
                <div style="flex: 1; min-width: 200px; background-color: #e1f5fe; padding: 15px; border-radius: 8px;">
                    <h4 style="margin-top: 0; color: #0277BD;">Images</h4>
                    <p style="font-size: 20px; font-weight: bold;">{summary.get("total_images", 0)}</p>
                    <p style="font-size: 14px; color: #555;">{summary.get("images_missing_alt_text", 0)} missing alt text</p>
                </div>
                <div style="flex: 1; min-width: 200px; background-color: #fff3e0; padding: 15px; border-radius: 8px;">
                    <h4 style="margin-top: 0; color: #E65100;">Font Issues</h4>
                    <p style="font-size: 20px; font-weight: bold;">{summary.get("slides_with_small_fonts", 0)} slides</p>
                    <p style="font-size: 14px; color: #555;">with small fonts</p>
                </div>
                <div style="flex: 1; min-width: 200px; background-color: #e8eaf6; padding: 15px; border-radius: 8px;">
                    <h4 style="margin-top: 0; color: #303F9F;">Text Complexity</h4>
                    <p style="font-size: 20px; font-weight: bold;">{summary.get("slides_with_complex_text", 0)} slides</p>
                    <p style="font-size: 14px; color: #555;">with complex text</p>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Display detailed issues
    with st.expander("View Detailed Accessibility Issues"):
        if "issues" in wcag_report:
            issues = wcag_report["issues"]
            
            # Alt text issues
            if issues.get("alt_text"):
                st.markdown("#### Alternative Text Issues")
                for issue in issues["alt_text"]:
                    st.markdown(
                        f"""
                        <div style="background-color: #ffebee; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                            <strong>Slide {issue['slide_num'] + 1}:</strong> {issue['issue']}
                            <br/><small>{issue.get('description', '')}</small>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
            
            # Font size issues
            if issues.get("font_size"):
                st.markdown("#### Font Size Issues")
                for issue in issues["font_size"]:
                    st.markdown(
                        f"""
                        <div style="background-color: #fff8e1; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                            <strong>Slide {issue['slide_num'] + 1}:</strong> {issue['issue']}
                            <br/><small>{issue.get('recommendation', '')}</small>
                            <br/><small>Text: "{issue.get('text', '')}"</small>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
            
            # Contrast issues
            if issues.get("contrast"):
                st.markdown("#### Contrast Issues")
                for issue in issues["contrast"]:
                    st.markdown(
                        f"""
                        <div style="background-color: #e3f2fd; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                            <strong>Slide {issue['slide_num'] + 1}:</strong> {issue['issue']}
                            <br/><small>{issue.get('description', '')}</small>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
            
            # Text complexity issues
            if issues.get("text_complexity"):
                st.markdown("#### Text Complexity Issues")
                for issue in issues["text_complexity"]:
                    st.markdown(
                        f"""
                        <div style="background-color: #e8f5e9; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                            <strong>Slide {issue['slide_num'] + 1}:</strong> {issue['issue']}
                            <br/><small>{issue.get('suggestion', '')}</small>
                            <br/><small>Text: "{issue.get('text', '')}"</small>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )

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
        
        st.markdown("""
        <div style="background-color: white; border-radius: 8px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <h4 style="margin-top: 0; color: #1565C0;">Font Accessibility</h4>
            <p style="color: #555; font-size: 0.9rem;">Increase font sizes to ensure readability for all users, including those with visual impairments.</p>
        </div>
        """, unsafe_allow_html=True)
        fix_font_size = st.checkbox("Fix Small Font Sizes", value=True)
        
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
    
    with col2:
        st.markdown("""
        <div style="background-color: white; border-radius: 8px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <h4 style="margin-top: 0; color: #1565C0;">Color Contrast</h4>
            <p style="color: #555; font-size: 0.9rem;">Improve text-to-background contrast to meet WCAG standards for better readability.</p>
        </div>
        """, unsafe_allow_html=True)
        improve_contrast = st.checkbox("Fix Color Contrast Issues", value=True)
        
        st.markdown("""
        <div style="background-color: white; border-radius: 8px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <h4 style="margin-top: 0; color: #1565C0;">Text Simplification</h4>
            <p style="color: #555; font-size: 0.9rem;">Simplify complex language to improve readability and comprehension using AI assistance.</p>
        </div>
        """, unsafe_allow_html=True)
        simplify_text = st.checkbox("Simplify Complex Text", value=True)
        
        # Add this to the enhancement options
        with st.expander("Advanced Options"):
            use_local_only = st.checkbox("Local-only mode (don't use Ollama)", 
                                        value=st.session_state.get('use_local_only', False))
            if use_local_only:
                st.info("Local-only mode enabled. Alt text will use basic placeholders instead of AI generation.")
            
            # Store in session state
            st.session_state['use_local_only'] = use_local_only
    
    return generate_alt_text, fix_font_size, improve_contrast, simplify_text

def display_enhance_button_and_process(generate_alt_text, fix_font_size=True, improve_contrast=True, simplify_text=True):
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
                    # Ensure the ppt_processor is in the session state
                    if 'ppt_processor' not in st.session_state or st.session_state.ppt_processor is None:
                        # If not, create a new one
                        from src.ppt_processor import PPTProcessor
                        st.session_state.ppt_processor = PPTProcessor()
                        st.session_state.ppt_processor.load_presentation(st.session_state.input_path)
                    
                    # Call enhancement function with explicit parameter list and processor
                    after_score = enhance_presentation_simple(
                        st.session_state.ppt_processor, 
                        [generate_alt_text, fix_font_size, improve_contrast, simplify_text]
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
                        # Enhancement returned None, meaning it failed
                        st.error("Enhancement process failed. Please check the error messages above.")
                        
                        # Add retry button
                        if st.button("Try again", key="retry_btn"):
                            st.session_state.enhance_button_pressed = False
                            st.experimental_rerun()
                    
            except Exception as e:
                st.error(f"Error enhancing presentation: {str(e)}")
                import traceback
                st.error(traceback.format_exc())

def display_enhancement_results(after_score):
    """Display the enhancement results with before and after comparison"""
    st.markdown("<h3 style='color: #2E7D32;'>Enhancement Results</h3>", unsafe_allow_html=True)
    
    # Make sure the required session state variables exist
    if 'before_score' not in st.session_state:
        st.error("Missing 'before_score' in session state. Cannot display comparison.")
        return
    
    # Check if after_score argument is valid, if not try to get from session state
    if after_score is None and 'after_score' in st.session_state:
        after_score = st.session_state.after_score
    
    # If still None, show error and return
    if after_score is None:
        st.error("Enhancement results are not available. The enhancement process may have failed.")
        return
        
    before_score = st.session_state.before_score
    
    # Create columns for before and after scores
    col1, col2 = st.columns(2)
    
    try:
        # Safely get overall scores with defaults if missing
        before_overall = before_score.get("overall_score", 0)
        after_overall = after_score.get("overall_score", 0)
        
        with col1:
            st.markdown("<h4>Before Enhancement</h4>", unsafe_allow_html=True)
            
            # Create a gauge chart for the before score
            before_fig = create_gauge_chart(
                before_overall, 
                "Overall Accessibility Score", 
                color='#FFA726'
            )
            st.plotly_chart(before_fig, use_container_width=True)
            
            # Display category scores
            st.markdown("#### Category Scores")
            before_cat_scores = before_score.get("category_scores", {})
            for cat in ["alt_text", "font_size", "contrast", "text_complexity"]:
                score = before_cat_scores.get(cat, 0)
                st.markdown(f"**{cat.replace('_', ' ').title()}:** {score}/100")
        
        with col2:
            st.markdown("<h4>After Enhancement</h4>", unsafe_allow_html=True)
            
            # Create a gauge chart for the after score
            after_fig = create_gauge_chart(
                after_overall, 
                "Overall Accessibility Score", 
                color='#66BB6A'
            )
            st.plotly_chart(after_fig, use_container_width=True)
            
            # Display category scores
            st.markdown("#### Category Scores")
            after_cat_scores = after_score.get("category_scores", {})
            for cat in ["alt_text", "font_size", "contrast", "text_complexity"]:
                after_score_val = after_cat_scores.get(cat, 0)
                before_score_val = before_cat_scores.get(cat, 0)
                improvement = after_score_val - before_score_val
                
                # Calculate improvement and display with color
                if improvement > 0:
                    st.markdown(f"**{cat.replace('_', ' ').title()}:** {after_score_val}/100 <span style='color:green'>(+{improvement})</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"**{cat.replace('_', ' ').title()}:** {after_score_val}/100")
        
        # Display overall improvement
        improvement = after_overall - before_overall
        if improvement > 0:
            st.success(f"Overall improvement: +{improvement} points")
        else:
            st.info("No significant score improvement detected.")
            
        # Only show download buttons if we have the enhanced file
        if 'enhanced_file_path' in st.session_state and os.path.exists(st.session_state.enhanced_file_path):
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
                if 'report_html' in st.session_state and st.session_state.report_html:
                    st.download_button(
                        label="📄 Download Accessibility Report",
                        data=st.session_state.report_html,
                        file_name="accessibility_report.html",
                        mime="text/html",
                        key="download_report_btn",
                        use_container_width=True
                    )
                else:
                    st.info("HTML report not available for download.")
        
        # Reset button
        if st.button("Start Over", key="reset_btn"):
            # Clear all relevant session state values
            for key in ['enhance_button_pressed', 'after_score', 'report_html']:
                if key in st.session_state:
                    del st.session_state[key]
            st.experimental_rerun()
            
    except Exception as e:
        import traceback
        st.error(f"Error displaying enhancement results: {str(e)}")
        st.error(traceback.format_exc())

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

def display_category_score(category, score):
    """Display a category score with appropriate styling"""
    
    # Determine color based on score
    if score >= 80:
        color = "#4CAF50"  # Green
        bg_color = "#E8F5E9"
    elif score >= 60:
        color = "#FF9800"  # Orange
        bg_color = "#FFF3E0"
    else:
        color = "#F44336"  # Red
        bg_color = "#FFEBEE"
    
    # Display score with styled container
    st.markdown(
        f"""
        <div style="background-color: {bg_color}; padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="margin-top: 0; margin-bottom: 5px;">{category}</h4>
            <div style="font-size: 24px; font-weight: bold; color: {color};">{score}</div>
        </div>
        """,
        unsafe_allow_html=True
    ) 