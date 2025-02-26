"""
Enhancement functionality for PowerPoint presentations.
Handles accessibility improvements.
"""

import streamlit as st
import shutil
import time
from src.utils import generate_report_html
from src.alt_text_generator import AltTextGenerator

def enhance_presentation_simple(ppt_processor, options):
    """Simplified enhancement that handles WMF image errors"""
    try:
        # Log the beginning of the enhancement process
        st.info("Starting enhancement process - this may take a moment...")
        
        # Make a copy of the presentation
        shutil.copy(st.session_state.input_path, st.session_state.output_path)
        
        # Load the copied presentation (important to work on the actual output file)
        ppt_processor.load_presentation(st.session_state.output_path)
        
        # Unpack options
        generate_alt_text, fix_font_size, improve_contrast, simplify_text = options
        
        # Check for local-only mode in session state
        use_local_only = st.session_state.get('use_local_only', False)
        
        # Initialize the alt text generator if needed
        alt_text_generator = None
        if generate_alt_text:
            alt_text_generator = AltTextGenerator()
            
            # Check if Ollama API is available
            api_available = not use_local_only and alt_text_generator.check_api_availability()
            if not api_available:
                st.warning("⚠️ Ollama API is not available or local-only mode is enabled. Alt text will use placeholders instead of AI-generated descriptions.")
        
        # Check for WMF images and handle them
        wmf_images = [img for img in ppt_processor.image_shapes if 'warning' in img and 'WMF' in img.get('warning', '')]
        
        if wmf_images:
            st.info(f"Detected {len(wmf_images)} WMF images that need special handling.")
        
        # Process non-WMF images for alt text
        non_wmf_images = [img for img in ppt_processor.image_shapes 
                          if not ('warning' in img and 'WMF' in img.get('warning', ''))]
        
        alt_text_count = 0
        if generate_alt_text:  # Alt text generation enabled
            progress_message = st.empty()
            total_images = len(non_wmf_images)
            
            for idx, img in enumerate(non_wmf_images):
                if not img.get("alt_text"):
                    # Add progress update
                    progress_message.info(f"Generating alt text for image {idx+1} of {total_images}")
                    
                    try:
                        slide_num = img["slide_num"]
                        shape = img["shape"]
                        
                        # Use LLaVA for alt text if available, otherwise use placeholder
                        if alt_text_generator and img.get("image_path") and api_available:
                            alt_text = alt_text_generator.generate_alt_text(img["image_path"])
                        else:
                            alt_text = alt_text_generator.generate_placeholder_text(img)
                        
                        # Debug info
                        print(f"Setting alt text for slide {slide_num+1}: '{alt_text}'")
                        
                        # Use the proper update_alt_text method instead of direct property access
                        success = ppt_processor.update_alt_text(slide_num, shape, alt_text)
                        if success:
                            print(f"Successfully set alt text for slide {slide_num+1}")
                            alt_text_count += 1
                        else:
                            print(f"Failed to set alt text for slide {slide_num+1}")
                            
                    except Exception as e:
                        st.error(f"Error adding alt text to image: {str(e)}")
            
            # Clear progress message
            progress_message.empty()
        
        # Fix font sizes if enabled
        font_fixes = 0
        if fix_font_size:
            for text_data in ppt_processor.text_shapes:
                try:
                    font_size = text_data.get("font_size")
                    if font_size and font_size < 18:
                        shape = text_data["shape"]
                        ppt_processor.update_font_size(shape, 18)
                        font_fixes += 1
                except Exception as e:
                    st.error(f"Error fixing font size: {str(e)}")
        
        # Save the enhanced presentation
        success = ppt_processor.save_presentation(st.session_state.output_path)
        if not success:
            st.error("Failed to save the enhanced presentation")
        else:
            print(f"Successfully saved enhanced presentation to {st.session_state.output_path}")
            
        st.session_state.enhanced_file_path = st.session_state.output_path
        
        # Create a completely new processor to analyze the enhanced file
        # This ensures we're looking at the actual saved file, not the in-memory version
        from src.ppt_processor import PPTProcessor 
        from src.analysis import analyze_with_processor
        
        output_processor = PPTProcessor()
        output_processor.load_presentation(st.session_state.output_path)
        
        # Re-analyze with the new processor
        after_score, after_wcag_report = analyze_with_processor(output_processor)
        
        # Store the after analysis results in session state
        st.session_state.after_score = after_score
        st.session_state.after_wcag_report = after_wcag_report
        
        # Create HTML report
        html_report = f"""
        <html>
        <head>
            <title>Accessibility Enhancement Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #2E7D32; }}
                .section {{ background: #E8F5E9; padding: 15px; border-radius: 8px; margin: 10px 0; }}
                .warning {{ background: #FFF3E0; padding: 15px; border-radius: 8px; margin: 10px 0; }}
                .comparison {{ display: flex; justify-content: space-between; }}
                .score-card {{ flex: 1; margin: 10px; padding: 15px; border-radius: 8px; background: #f5f5f5; }}
                .improvement {{ color: green; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>PowerPoint Accessibility Report</h1>
            
            <div class="section">
                <h3>Accessibility Improvements</h3>
                <p>Your presentation has been enhanced with several accessibility improvements.</p>
                <ul>
                    <li><strong>Alt Text Added:</strong> {alt_text_count} images received alternative text {f"using AI vision model (LLaVA)" if api_available else "(using placeholders due to unavailable AI service)"}</li>
                    <li><strong>Font Size Fixed:</strong> {font_fixes} text elements with small fonts were adjusted</li>
                </ul>
            </div>
            
            <div class="section">
                <h3>Score Comparison</h3>
                <div class="comparison">
                    <div class="score-card">
                        <h4>Before</h4>
                        <p>Overall: {st.session_state.before_score["overall_score"]}/100</p>
                        <p>Alt Text: {st.session_state.before_score["category_scores"]["alt_text"]}/100</p>
                        <p>Font Size: {st.session_state.before_score["category_scores"]["font_size"]}/100</p>
                    </div>
                    <div class="score-card">
                        <h4>After</h4>
                        <p>Overall: {after_score["overall_score"]}/100</p>
                        <p>Alt Text: {after_score["category_scores"]["alt_text"]}/100</p>
                        <p>Font Size: {after_score["category_scores"]["font_size"]}/100</p>
                    </div>
                </div>
                <p class="improvement">Improvement: {after_score["overall_score"] - st.session_state.before_score["overall_score"]} points</p>
            </div>
            
            {f'<div class="warning"><h3>Special Image Formats</h3><p>Found {len(wmf_images)} WMF/EMF image(s) that were handled as special cases. These image formats may need manual review.</p></div>' if wmf_images else ''}
        </body>
        </html>
        """
        
        st.session_state.report_html = html_report
        
        return after_score
        
    except Exception as e:
        # Log error
        st.error(f"Enhancement error: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        
        return None 