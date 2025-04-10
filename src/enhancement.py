"""
Enhancement functionality for PowerPoint presentations.
Handles accessibility improvements with modular approach.
"""

import streamlit as st
import shutil
import time
import os
from src.utils import generate_report_html
from src.alt_text_generator import AltTextGenerator
import re

def enhance_presentation_simple(ppt_processor, options):
    """Enhanced PowerPoint accessibility with modular approach"""
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
        
        # MODULE 1: ALT TEXT GENERATION
        if generate_alt_text:
            process_alt_text_generation(ppt_processor, use_local_only)
        
        # MODULE 2: FONT SIZE IMPROVEMENT
        if fix_font_size:
            process_font_size_fixes(ppt_processor)
        
        # MODULE 3: CONTRAST IMPROVEMENT
        if improve_contrast:
            process_contrast_improvement(ppt_processor)
        
        # MODULE 4: TEXT SIMPLIFICATION
        if simplify_text:
            process_text_simplification(ppt_processor, use_local_only)
        
        # Save the final presentation
        ppt_processor.save_presentation(st.session_state.output_path)
        
        # Analyze the enhanced presentation to get updated scores
        from src.analysis import analyze_from_path
        
        # Create a new processor for accurate scoring
        from src.ppt_processor import PPTProcessor
        output_processor = PPTProcessor()
        output_processor.load_presentation(st.session_state.output_path)
        
        # Analyze with the new processor
        after_score, after_wcag_report = analyze_from_path(st.session_state.output_path)
        
        # Store the after analysis results in session state
        st.session_state.after_score = after_score
        st.session_state.after_wcag_report = after_wcag_report
        
        # Create HTML report
        from src.utils import generate_report_html
        html_report = generate_report_html(
            st.session_state.before_score, 
            after_score,
            st.session_state.wcag_report,
            after_wcag_report,
            len(process_wmf_images(ppt_processor))
        )
        
        # Store the report
        st.session_state.report_html = html_report
        
        # Return the score report instead of a boolean
        return after_score
        
    except Exception as e:
        st.error(f"Error during enhancement: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None

# MODULE 1: ALT TEXT GENERATION PROCESSING
def process_alt_text_generation(ppt_processor, use_local_only=False):
    """Process alt text generation for all images in the presentation"""
    # Initialize the alt text generator
    alt_text_generator = AltTextGenerator()
    
    # Check if Ollama API is available
    api_available = not use_local_only and alt_text_generator.check_api_availability()
    if not api_available:
        st.warning("⚠️ Ollama API is not available or local-only mode is enabled. Alt text will use placeholders instead of AI-generated descriptions.")
    
    # Prepare for batch processing
    non_wmf_images = [img for img in ppt_processor.image_shapes 
                     if not ('warning' in img and 'WMF' in img.get('warning', ''))]
    
    # Display progress
    progress_message = st.empty()
    total_images = len(non_wmf_images)
    
    if total_images == 0:
        progress_message.info("No compatible images found in the presentation.")
        return
    
    # STEP 1: Create a robust dictionary to track which slides have valid images
    slides_with_images = create_image_slide_map(non_wmf_images)
    
    # STEP 2: Generate alt text and update in presentation
    alt_text_count = generate_and_update_alt_text(
        ppt_processor, 
        non_wmf_images, 
        alt_text_generator, 
        api_available, 
        progress_message
    )
    
    # STEP 3: Add captions
    caption_count = add_image_captions(
        ppt_processor, 
        non_wmf_images, 
        slides_with_images,
        progress_message
    )
    
    # Clear progress message
    progress_message.empty()
    
    # Show success messages
    if alt_text_count > 0:
        st.success(f"✅ Added or improved alt text for {alt_text_count} images.")
    
    if caption_count > 0:
        st.success(f"✅ Added {caption_count} visible image captions.")

def create_image_slide_map(image_list):
    """Create a map of slides with valid images"""
    slides_with_images = {}
    
    for img in image_list:
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
    
    # Debug information
    for slide_num, images in slides_with_images.items():
        print(f"Slide {slide_num+1} has {len(images)} valid image(s)")
    
    return slides_with_images

def generate_and_update_alt_text(ppt_processor, image_list, alt_text_generator, api_available, progress_message):
    """Generate and update alt text for all images"""
    alt_text_count = 0
    
    # Identify single images per slide for special treatment
    slide_image_count = {}
    for img in image_list:
        slide_num = img["slide_num"]
        if slide_num not in slide_image_count:
            slide_image_count[slide_num] = 0
        slide_image_count[slide_num] += 1
    
    # Always process images individually to ensure consistency
    for idx, img in enumerate(image_list):
        progress_message.info(f"Processing image {idx+1} of {len(image_list)}")
        
        slide_num = img["slide_num"]
        shape = img["shape"]
        existing_alt_text = img.get("alt_text", "")
        
        # Check if this is a single image on a slide - give it special treatment
        is_single_image = slide_image_count[slide_num] == 1
        
        # Check if existing alt text is missing, empty, just whitespace, or a known placeholder
        if not existing_alt_text or \
           not existing_alt_text.strip() or \
           existing_alt_text == 'Description automatically generated' or \
           "automatically generated" in existing_alt_text.lower():
            
            print(f"Generating new alt text for image on slide {slide_num+1} (Existing: '{existing_alt_text}')")
            
            if alt_text_generator and img.get("image_path") and api_available:
                # For single images, request more detailed descriptions
                if is_single_image:
                    alt_text = alt_text_generator.generate_alt_text(img["image_path"], detailed=True)
                    print(f"Generated detailed alt text for single image on slide {slide_num+1}")
                else:
                    alt_text = alt_text_generator.generate_alt_text(img["image_path"])
            else:
                # Use more descriptive placeholder text, especially for single images
                if is_single_image:
                    alt_text = f"Primary image on slide {slide_num+1} showing visual content central to the slide's message and topic"
                    print(f"Using enhanced placeholder text for single image on slide {slide_num+1}")
                else:
                    alt_text = f"Image on slide {slide_num+1} containing visual content related to the slide topic"
                    print(f"Using enhanced placeholder text for slide {slide_num+1}")
            
            # Make sure single images have substantial alt text
            if is_single_image and len(alt_text.split()) < 10:
                alt_text += " This image is the primary visual element on this slide and conveys key information related to the slide content."
            
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
            # For single images, ensure existing alt text is substantial
            if is_single_image and len(existing_alt_text.split()) < 15:
                enhanced_alt_text = existing_alt_text + " This image is the primary visual element on this slide and conveys key information related to the slide content."
                success = ppt_processor.update_alt_text(slide_num, shape, enhanced_alt_text)
                if success:
                    img["alt_text"] = enhanced_alt_text
                    alt_text_count += 1
                    print(f"Enhanced existing alt text for single image on slide {slide_num+1}")
            else:
                # Existing alt text is considered potentially useful, keep it
                print(f"Keeping existing alt text found for image on slide {slide_num+1}: '{existing_alt_text}'")
    
    return alt_text_count

def add_image_captions(ppt_processor, image_list, slides_with_images, progress_message):
    """Add visible captions to images"""
    caption_count = 0
    
    progress_message.info("Adding image captions...")
    
    # Go through each slide and determine if it has a single image
    slide_image_count = {}
    for img in image_list:
        slide_num = img["slide_num"]
        if slide_num not in slide_image_count:
            slide_image_count[slide_num] = 0
        slide_image_count[slide_num] += 1
    
    # Process all images
    for idx, img in enumerate(image_list):
        try:
            slide_num = img["slide_num"]
            shape = img["shape"]
            
            # More reliable single-image detection
            is_single_image = slide_image_count[slide_num] == 1
            
            # Get the alt text (either existing or generated)
            alt_text = img.get("alt_text", "")
            if not alt_text or alt_text.strip() == "":
                # If alt text is missing, use a descriptive placeholder
                alt_text = f"Image on slide {slide_num+1} containing visual content related to the slide topic"
                
                # Also update the alt text property of the image
                ppt_processor.update_alt_text(slide_num, shape, alt_text)
                print(f"Added placeholder alt text for image on slide {slide_num+1}")
            
            # Debug for better troubleshooting
            print(f"Adding caption to image on slide {slide_num+1} - Single image: {is_single_image}")
            
            # Create caption text - use a more descriptive format
            caption_text = f"Image Description: {alt_text}"
            
            # Always use the primary caption function for consistency
            caption = ppt_processor.add_visible_caption(slide_num, shape, caption_text, is_single_image)
            if caption:
                caption_count += 1
                print(f"Successfully added caption to image on slide {slide_num+1}")
            else:
                # If the first attempt fails, try again with the simple caption as fallback
                print(f"Retrying caption for image on slide {slide_num+1} with simple method")
                caption = ppt_processor.add_simple_caption(slide_num, shape, caption_text)
                if caption:
                    caption_count += 1
                    print(f"Successfully added caption using simple method on slide {slide_num+1}")
                else:
                    print(f"Failed to add caption even with simple method on slide {slide_num+1}")
        except Exception as e:
            print(f"Error adding caption: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    return caption_count

# MODULE 2: FONT SIZE IMPROVEMENT
def process_font_size_fixes(ppt_processor):
    """Process font size improvements"""
    progress_message = st.empty()
    progress_message.info("Improving font sizes for better readability...")
    
    font_fixes = 0
    min_readable_size = 18  # Minimum readable font size in points
    
    for text_data in ppt_processor.text_shapes:
        # Skip empty text or text that's already large enough
        if not text_data["text"].strip():
            continue
            
        shape = text_data["shape"]
        current_size = text_data.get("font_size")
        
        if current_size and current_size < min_readable_size:
            if ppt_processor.update_font_size(shape, min_readable_size):
                font_fixes += 1
    
    progress_message.empty()
    
    if font_fixes > 0:
        st.success(f"✅ Improved font sizes for {font_fixes} text elements for better readability.")

# MODULE 3: CONTRAST IMPROVEMENT
def process_contrast_improvement(ppt_processor):
    """Process contrast improvements"""
    from src.accessibility_checker import AccessibilityChecker
    
    progress_message = st.empty()
    progress_message.info("Improving text contrast...")
    
    accessibility_checker = AccessibilityChecker()
    contrast_fixes = 0
    errors = 0
    
    # Process each text shape
    for text_data in ppt_processor.text_shapes:
        shape = text_data["shape"]
        
        # Skip if no text
        if not text_data["text"].strip():
            continue
            
        try:
            # Check if the shape has color information that can be modified
            if not hasattr(shape, 'fill') or not hasattr(shape, 'font'):
                print(f"Skipping shape without fill or font attributes")
                continue
                
            # Make text darker (majority of slides have light backgrounds)
            if ppt_processor.update_text_contrast(shape, make_darker=True):
                contrast_fixes += 1
        except AttributeError as ae:
            # Log specific color type errors
            error_msg = str(ae)
            if "no .rgb property" in error_msg or "'RGBColor' object has no attribute" in error_msg:
                print(f"Color type error: {error_msg}")
                errors += 1
            else:
                print(f"Attribute error updating text contrast: {error_msg}")
            continue
        except Exception as e:
            # Log error but continue processing other shapes
            print(f"Error updating text contrast: {str(e)}")
            errors += 1
            continue
    
    progress_message.empty()
    
    if contrast_fixes > 0:
        st.success(f"✅ Improved contrast for {contrast_fixes} text elements.")
    else:
        st.info("No contrast improvements were made. Your presentation may already have good contrast, or text colors couldn't be modified.")
    
    if errors > 0:
        st.warning(f"Note: {errors} text elements were skipped due to unsupported color formats.")

# MODULE 4: TEXT SIMPLIFICATION
def process_text_simplification(ppt_processor, use_local_only=False):
    """Process text simplification"""
    from src.text_simplifier import TextSimplifier
    
    progress_message = st.empty()
    progress_message.info("Simplifying complex text...")
    
    text_simplifier = TextSimplifier()
    
    # Check if Ollama API is available
    api_available = not use_local_only and text_simplifier.check_api_availability()
    if not api_available:
        st.warning("⚠️ Ollama API is not available or local-only mode is enabled. Text simplification will be limited.")
    
    simplifications = 0
    simplified_list = []
    skipped = 0
    
    # Go through all text elements
    complex_texts = []
    for text_data in ppt_processor.text_shapes:
        text = text_data["text"]
        
        # Skip auto-generated content or captions we added
        if text.startswith("Image Description:") or "This image" in text:
            continue
            
        # Skip if no text or text is too short to need simplification
        if not text.strip() or len(text.split()) < 15:
            continue
            
        # Check if text is complex using stricter criteria
        # Only select truly complex text to avoid over-simplification
        words = text.split()
        avg_word_length = sum(len(word) for word in words) / max(1, len(words))
        complex_words = sum(1 for w in words if len(w) > 6)
        complex_word_ratio = complex_words / max(1, len(words))
        
        # Only simplify text that is truly complex by multiple measures
        if ((avg_word_length > 6.8) or 
            (complex_word_ratio > 0.3 and len(words) > 15) or
            (len(words) > 35 and text.count('\n') < 2)):
            
            complex_texts.append((text_data["slide_num"], text_data["shape"], text))
    
    total_complex = len(complex_texts)
    if total_complex > 0:
        print(f"Found {total_complex} complex text elements to simplify")
    
    # Process complex texts
    for slide_num, shape, text in complex_texts:
        try:
            # Simplify the text
            if api_available:
                simplified_text = text_simplifier.simplify_text(text)
            else:
                # Use basic simplification if API not available
                simplified_text = text_simplifier.basic_simplify(text)
            
            # Only apply simplification if it actually improves complexity
            if simplified_text and simplified_text != text:
                # Check if simplified text is actually less complex
                improvement_score = calculate_simplification_improvement(text, simplified_text)
                
                # Only apply if there's a meaningful improvement (at least 15%)
                if improvement_score >= 15:
                    if ppt_processor.update_text(shape, simplified_text):
                        simplifications += 1
                        simplified_list.append({
                            "slide_num": slide_num,
                            "original": text[:100] + "..." if len(text) > 100 else text,
                            "simplified": simplified_text[:100] + "..." if len(simplified_text) > 100 else simplified_text,
                            "improvement": improvement_score
                        })
                        print(f"Successfully simplified text on slide {slide_num+1} (improvement: {improvement_score}%)")
                else:
                    # Skip if simplification didn't improve complexity enough
                    skipped += 1
                    print(f"Skipped text on slide {slide_num+1} as simplification didn't improve complexity enough (score: {improvement_score}%)")
        except Exception as e:
            print(f"Error simplifying text on slide {slide_num+1}: {str(e)}")
    
    progress_message.empty()
    
    if simplifications > 0:
        st.success(f"✅ Simplified {simplifications} complex text elements for better readability.")
    
    if skipped > 0:
        st.info(f"Skipped {skipped} texts where simplification wouldn't significantly improve readability.")
        
    return simplified_list

def calculate_simplification_improvement(original, simplified):
    """Calculate a percentage improvement score between original and simplified text"""
    # Compare word length
    orig_words = original.split()
    simp_words = simplified.split()
    
    if len(orig_words) == 0 or len(simp_words) == 0:
        return 0
    
    # Calculate basic metrics
    orig_avg_word_len = sum(len(word) for word in orig_words) / len(orig_words)
    simp_avg_word_len = sum(len(word) for word in simp_words) / len(simp_words)
    
    # Count complex words (>6 characters)
    orig_complex_words = sum(1 for w in orig_words if len(w) > 6)
    simp_complex_words = sum(1 for w in simp_words if len(w) > 6)
    
    orig_complex_ratio = orig_complex_words / max(1, len(orig_words))
    simp_complex_ratio = simp_complex_words / max(1, len(simp_words))
    
    # Calculate sentence length metrics
    orig_sentences = [s for s in re.split(r'[.!?]+', original) if s.strip()]
    simp_sentences = [s for s in re.split(r'[.!?]+', simplified) if s.strip()]
    
    orig_avg_sent_len = len(orig_words) / max(1, len(orig_sentences))
    simp_avg_sent_len = len(simp_words) / max(1, len(simp_sentences))
    
    # Calculate percentage improvements for each metric
    word_len_improvement = max(0, (orig_avg_word_len - simp_avg_word_len) / orig_avg_word_len * 100)
    complex_ratio_improvement = max(0, (orig_complex_ratio - simp_complex_ratio) / max(0.01, orig_complex_ratio) * 100)
    sent_len_improvement = max(0, (orig_avg_sent_len - simp_avg_sent_len) / orig_avg_sent_len * 100)
    
    # Overall improvement is a weighted average of the three metrics
    # with more weight given to reducing complex words and sentence length
    overall_improvement = (
        word_len_improvement * 0.3 +
        complex_ratio_improvement * 0.4 +
        sent_len_improvement * 0.3
    )
    
    # Cap improvement at 100% and ensure text is not much longer
    text_length_penalty = max(0, (len(simplified) - len(original) * 1.1) / (len(original) * 0.1) * 20)
    
    final_score = max(0, min(100, overall_improvement - text_length_penalty))
    return int(final_score)

def process_wmf_images(ppt_processor):
    """Process WMF images that need special handling"""
    wmf_images = [img for img in ppt_processor.image_shapes if 'warning' in img and 'WMF' in img.get('warning', '')]
    
    if wmf_images:
        st.info(f"Detected {len(wmf_images)} WMF images that need special handling.")
        
        # Add notes about WMF images in the presentation
        for img in wmf_images:
            slide_num = img.get("slide_num", 0)
            shape = img.get("shape")
            
            if shape:
                # Try to update alt text to indicate it's a WMF image
                alt_text = f"Windows Metafile (WMF) image on slide {slide_num+1} - Consider replacing with a more accessible format."
                ppt_processor.update_alt_text(slide_num, shape, alt_text)
                
                # Add a visible note below the image
                ppt_processor.add_simple_caption(slide_num, shape, 
                    "This image is in Windows Metafile (WMF) format, which may have limited accessibility.")
    
    # Return the WMF images list instead of just the count
    return wmf_images 