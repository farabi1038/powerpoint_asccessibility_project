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
        
        # Initialize the text simplifier if needed
        text_simplifier = None
        if simplify_text:
            from src.text_simplifier import TextSimplifier
            text_simplifier = TextSimplifier()
            
            # Check if Ollama API is available
            api_available = not use_local_only and text_simplifier.check_api_availability()
            if not api_available:
                st.warning("⚠️ Ollama API is not available or local-only mode is enabled. Text simplification will be limited.")
        
        # Initialize the accessibility checker for contrast fixes
        if improve_contrast:
            from src.accessibility_checker import AccessibilityChecker
            accessibility_checker = AccessibilityChecker()
        
        # Check for WMF images and handle them
        wmf_images = [img for img in ppt_processor.image_shapes if 'warning' in img and 'WMF' in img.get('warning', '')]
        
        if wmf_images:
            st.info(f"Detected {len(wmf_images)} WMF images that need special handling.")
        
        # Process non-WMF images for alt text
        non_wmf_images = [img for img in ppt_processor.image_shapes
                          if not ('warning' in img and 'WMF' in img.get('warning', ''))]
        
        alt_text_count = 0
        caption_count = 0
        
        if generate_alt_text:  # Alt text generation enabled
            progress_message = st.empty()
            total_images = len(non_wmf_images)
            
            # Debug info
            print(f"Total images to process: {total_images}")
            
            # STEP 1: Create a more robust dictionary to track which slides have valid images
            slides_with_images = {}
            for img in non_wmf_images:
                slide_num = img.get('slide_num')
                shape = img.get('shape')
                
                # Ensure shape is actually a picture (MsoShapeType.PICTURE = 13)
                if shape is not None and hasattr(shape, 'shape_type'):
                    if shape.shape_type != 13:
                        print(f"Skipping shape on slide {slide_num+1} - shape_type {shape.shape_type} is not an image.")
                        continue
                else:
                    print(f"Skipping shape on slide {slide_num+1} - no valid shape or shape_type.")
                    continue
                
                if slide_num not in slides_with_images:
                    slides_with_images[slide_num] = []
                slides_with_images[slide_num].append(img)
            
            # Debug the detected slides with images
            for slide_num, images in slides_with_images.items():
                print(f"Slide {slide_num+1} has {len(images)} valid image(s)")
            
            # STEP 2: First pass - Generate alt text
            for idx, img in enumerate(non_wmf_images):
                progress_message.info(f"Processing image {idx+1} of {total_images}")
                try:
                    slide_num = img["slide_num"]
                    shape = img["shape"]
                    existing_alt_text = img.get("alt_text", "")

                    # Extra debug for single-slide or single-image detection
                    single_slide = (len(slides_with_images) == 1)
                    single_image_on_slide = (len(slides_with_images.get(slide_num, [])) == 1)
                    print(f"Slide {slide_num+1} - Single slide in deck? {single_slide}, Single image on slide? {single_image_on_slide}")

                    print(f"Processing image {idx+1} on slide {slide_num+1} for alt text generation")

                    # Check if existing alt text is missing, empty, just whitespace, or a known placeholder
                    if not existing_alt_text or \
                       not existing_alt_text.strip() or \
                       existing_alt_text == 'Description automatically generated':
                        # Existing alt text is unhelpful or missing, proceed with generation
                        print(f"Generating new alt text for image on slide {slide_num+1} (Existing: '{existing_alt_text}')")
                        if alt_text_generator and img.get("image_path") and api_available:
                            alt_text = alt_text_generator.generate_alt_text(img["image_path"])
                        else:
                            # Fallback to placeholder if conditions not met
                            alt_text = alt_text_generator.generate_placeholder_text(img)
                            print(f"Falling back to placeholder text for slide {slide_num+1}")

                        # Update alt text in the presentation object
                        success = ppt_processor.update_alt_text(slide_num, shape, alt_text)
                        if success:
                            # Store the potentially new alt text back in the image object for captioning
                            img["alt_text"] = alt_text 
                            alt_text_count += 1
                            print(f"Alt text generated and applied for image on slide {slide_num+1}")
                        else:
                            print(f"Failed to apply alt text for image on slide {slide_num+1}")
                    else:
                        # Existing alt text is considered potentially useful, keep it
                        print(f"Keeping existing alt text found for image on slide {slide_num+1}: '{existing_alt_text}'")

                except Exception as e:
                    print(f"Error generating alt text: {str(e)}")
            
            # Second pass: Add visible captions to all images
            for idx, img in enumerate(non_wmf_images):
                try:
                    slide_num = img["slide_num"]
                    shape = img["shape"]
                    
                    # Get the alt text (either existing or generated)
                    alt_text = img.get("alt_text", "")
                    if not alt_text:
                        # If somehow alt text is still missing, use a placeholder
                        alt_text = f"Image on slide {slide_num+1}"
                    
                    # IMPROVED: Make detection of single images more robust
                    is_single_image = len(slides_with_images.get(slide_num, [])) == 1
                    
                    # Debug for better troubleshooting
                    print(f"Adding caption to image on slide {slide_num+1} - Single image: {is_single_image}")
                    
                    # Create caption text
                    caption_text = f"Image Description: {alt_text}"
                    
                    # IMPROVED: Force the caption to be properly added and make special handling for single images
                    caption = ppt_processor.add_visible_caption(slide_num, shape, caption_text, is_single_image)
                    if caption:
                        caption_count += 1
                        print(f"Successfully added caption to image on slide {slide_num+1}")
                    else:
                        # If the first attempt fails for a single image, try again with different parameters
                        if is_single_image:
                            print(f"Retrying caption for single image on slide {slide_num+1}")
                            # Try a different placement approach
                            caption = ppt_processor.add_simple_caption(slide_num, shape, caption_text)
                            if caption:
                                caption_count += 1
                                print(f"Successfully added caption using simple method on slide {slide_num+1}")
                            else:
                                print(f"Failed to add caption even with simple method on slide {slide_num+1}")
                        else:
                            print(f"Failed to add caption to image on slide {slide_num+1}")
                except Exception as e:
                    print(f"Error adding caption: {str(e)}")
                    import traceback
                    print(traceback.format_exc())
            
            # Clear progress message
            progress_message.empty()
            
            # Show success for captions
            if caption_count > 0:
                st.success(f"✅ Added {caption_count} visible image captions below images.")
        
        # Fix font sizes if enabled
        font_fixes = 0
        if fix_font_size:
            progress_message = st.empty()
            progress_message.info("Improving font sizes for better readability...")
            
            for text_data in ppt_processor.text_shapes:
                try:
                    font_size = text_data.get("font_size")
                    if font_size and font_size < 18:
                        shape = text_data["shape"]
                        slide_num = text_data["slide_num"]
                        
                        print(f"Fixing font size on slide {slide_num+1} from {font_size}pt to 18pt")
                        if ppt_processor.update_font_size(shape, 18):
                            font_fixes += 1
                            print(f"Successfully fixed font size on slide {slide_num+1}")
                        else:
                            print(f"No font size changes needed on slide {slide_num+1}")
                except Exception as e:
                    print(f"Error fixing font size: {str(e)}")
            
            progress_message.empty()
            
            # Show success message for font fixes
            if font_fixes > 0:
                st.success(f"✅ Increased font size for {font_fixes} text elements to improve readability.")
        
        # Fix contrast issues if enabled
        contrast_fixes = 0
        if improve_contrast:
            progress_message = st.empty()
            progress_message.info("Improving text contrast for better readability...")
            
            # IMPROVED: Only fix contrast for text that's too light against light backgrounds
            # Detect background color first (simplified approach)
            background_is_light = True  # Assume light background
            
            # First, let's handle text shapes with more careful approach
            for text_data in ppt_processor.text_shapes:
                try:
                    # Skip if no text
                    if not text_data.get("text"):
                        continue
                        
                    # Get the shape
                    shape = text_data["shape"]
                    slide_num = text_data["slide_num"]
                    
                    # Skip very small text or empty text
                    if not text_data.get("text").strip() or text_data.get("font_size", 0) < 8:
                        continue
                    
                    # Use our simplified contrast fixing method - only for text that needs it
                    if background_is_light:
                        # For light backgrounds, make text darker for better contrast
                        print(f"Improving contrast on slide {slide_num+1}")
                        if ppt_processor.update_text_contrast(shape, make_darker=True):
                            contrast_fixes += 1
                            print(f"Fixed contrast on slide {slide_num+1}")
                        else:
                            print(f"No contrast changes needed on slide {slide_num+1}")
                except Exception as e:
                    print(f"Error fixing contrast: {str(e)}")
            
            progress_message.empty()
            
            # Show success message for contrast fixes
            if contrast_fixes > 0:
                st.success(f"✅ Improved contrast for {contrast_fixes} text elements to meet WCAG standards.")
        
        # Simplify complex text if enabled
        text_simplifications = 0
        if simplify_text and text_simplifier:
            # First, check if we need to simplify any text
            complex_texts = []
            for text_data in ppt_processor.text_shapes:
                text = text_data.get("text", "")
                if text:
                    words = text.split()
                    if words:
                        avg_word_length = sum(len(word) for word in words) / len(words)
                        if avg_word_length > 6 or len(words) > 25:
                            # Add shape index for batch processing
                            text_data_copy = text_data.copy()
                            text_data_copy["shape_idx"] = text_data_copy.get("shape_idx", 0)
                            complex_texts.append(text_data_copy)
            
            if complex_texts:
                # Process complex texts in batch
                progress_message = st.empty()
                progress_message.info(f"Simplifying {len(complex_texts)} complex text elements...")
                
                # Get simplified texts
                simplified_texts = text_simplifier.batch_simplify_text(complex_texts)
                
                # Update the presentation with simplified texts
                for text_data in complex_texts:
                    key = f"{text_data['slide_num']}_{text_data.get('shape_idx', 0)}"
                    if key in simplified_texts:
                        simplified = simplified_texts[key]["simplified"]
                        original = simplified_texts[key]["original"]
                        
                        if simplified != original:
                            shape = text_data["shape"]
                            
                            # Update text in the shape
                            if hasattr(shape, "text_frame"):
                                try:
                                    # Store all original paragraph formatting
                                    paragraph_formats = []
                                    for para in shape.text_frame.paragraphs:
                                        # Store alignment and other paragraph-level properties
                                        para_format = {
                                            "alignment": para.alignment if hasattr(para, "alignment") else None,
                                            "level": para.level if hasattr(para, "level") else 0,
                                            "space_before": para.space_before if hasattr(para, "space_before") else None,
                                            "space_after": para.space_after if hasattr(para, "space_after") else None,
                                            "line_spacing": para.line_spacing if hasattr(para, "line_spacing") else None,
                                            "runs": []
                                        }
                                        
                                        # Store formatting for each run
                                        for run in para.runs:
                                            run_format = {"text": run.text}
                                            if hasattr(run, "font"):
                                                font = run.font
                                                if hasattr(font, "size"):
                                                    run_format["size"] = font.size
                                                if hasattr(font, "bold"):
                                                    run_format["bold"] = font.bold
                                                if hasattr(font, "italic"):
                                                    run_format["italic"] = font.italic
                                                if hasattr(font, "underline"):
                                                    run_format["underline"] = font.underline
                                                if hasattr(font, "color") and font.color and hasattr(font.color, "rgb"):
                                                    run_format["color"] = font.color.rgb
                                                if hasattr(font, "name"):
                                                    run_format["name"] = font.name
                                            para_format["runs"].append(run_format)
                                        
                                        paragraph_formats.append(para_format)
                                    
                                    # Now we need to carefully update the text while preserving formatting
                                    # First, clear the entire text frame
                                    while len(shape.text_frame.paragraphs) > 0:
                                        if len(shape.text_frame.paragraphs) == 1:
                                            # Can't remove the last paragraph, just clear it
                                            p = shape.text_frame.paragraphs[0]
                                            p.clear()
                                            
                                            # Add the simplified text as a single run
                                            run = p.add_run()
                                            run.text = simplified
                                            
                                            # Apply formatting from the first run of the first paragraph
                                            if paragraph_formats and paragraph_formats[0]["runs"]:
                                                first_run_format = paragraph_formats[0]["runs"][0]
                                                
                                                # Apply font properties if they exist
                                                try:
                                                    if "size" in first_run_format:
                                                        run.font.size = first_run_format["size"]
                                                    if "bold" in first_run_format:
                                                        run.font.bold = first_run_format["bold"]
                                                    if "italic" in first_run_format:
                                                        run.font.italic = first_run_format["italic"]
                                                    if "underline" in first_run_format:
                                                        run.font.underline = first_run_format["underline"]
                                                    if "color" in first_run_format:
                                                        run.font.color.rgb = first_run_format["color"]
                                                    if "name" in first_run_format:
                                                        run.font.name = first_run_format["name"]
                                                except Exception as format_error:
                                                    print(f"Error applying font format: {format_error}")
                                            
                                            # Apply paragraph formatting
                                            if paragraph_formats:
                                                first_para_format = paragraph_formats[0]
                                                
                                                try:
                                                    if first_para_format["alignment"] is not None:
                                                        p.alignment = first_para_format["alignment"]
                                                    p.level = first_para_format["level"]
                                                    if first_para_format["space_before"] is not None:
                                                        p.space_before = first_para_format["space_before"]
                                                    if first_para_format["space_after"] is not None:
                                                        p.space_after = first_para_format["space_after"]
                                                    if first_para_format["line_spacing"] is not None:
                                                        p.line_spacing = first_para_format["line_spacing"]
                                                except Exception as para_format_error:
                                                    print(f"Error applying paragraph format: {para_format_error}")
                                            
                                            break
                                        else:
                                            # Remove non-last paragraphs
                                            try:
                                                shape.text_frame._p.remove(shape.text_frame.paragraphs[-1]._p)
                                            except:
                                                # If we can't remove it, just stop and use what we have
                                                break
                                            
                                    text_simplifications += 1
                                    print(f"Successfully simplified text on slide {text_data['slide_num']+1}")
                                except Exception as e:
                                    print(f"Error updating simplified text: {e}")
                                    import traceback
                                    print(traceback.format_exc())
                
                progress_message.empty()
        
        # Save the enhanced presentation
        success = ppt_processor.save_presentation(st.session_state.output_path)
        if not success:
            st.error("Failed to save the enhanced presentation")
        else:
            print(f"Successfully saved enhanced presentation to {st.session_state.output_path}")
            
            # Add a success message specifically about captions if any were added
            if caption_count > 0:
                st.success(f"✅ Added {caption_count} visible image captions to make images more accessible.")
            
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
                    <li><strong>Visible Captions Added:</strong> {caption_count} images received visible captions</li>
                    <li><strong>Font Size Fixed:</strong> {font_fixes} text elements with small fonts were adjusted</li>
                    <li><strong>Contrast Fixed:</strong> {contrast_fixes} text elements had their contrast improved</li>
                    <li><strong>Text Simplified:</strong> {text_simplifications} complex text elements were simplified</li>
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
                        <p>Contrast: {st.session_state.before_score["category_scores"]["contrast"]}/100</p>
                        <p>Text Complexity: {st.session_state.before_score["category_scores"]["text_complexity"]}/100</p>
                    </div>
                    <div class="score-card">
                        <h4>After</h4>
                        <p>Overall: {after_score["overall_score"]}/100</p>
                        <p>Alt Text: {after_score["category_scores"]["alt_text"]}/100</p>
                        <p>Font Size: {after_score["category_scores"]["font_size"]}/100</p>
                        <p>Contrast: {after_score["category_scores"]["contrast"]}/100</p>
                        <p>Text Complexity: {after_score["category_scores"]["text_complexity"]}/100</p>
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