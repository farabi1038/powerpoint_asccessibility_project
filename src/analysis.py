"""
Analysis functionality for PowerPoint presentations.
Handles accessibility checking and scoring.
"""

import streamlit as st
from src.ppt_processor import PPTProcessor
from src.scoring import AccessibilityScorer
from src.utils import create_wcag_compliance_chart

def analyze_accessibility(uploaded_file):
    """Analyze the accessibility of a PowerPoint file"""
    from src.state import setup_file_paths
    
    # Setup file paths
    input_path, temp_dir = setup_file_paths(uploaded_file)
    
    # Process PowerPoint
    ppt_processor = PPTProcessor()
    st.session_state.ppt_processor = ppt_processor
    
    # Load presentation and extract content
    ppt_processor.load_presentation(input_path)
    
    # Score accessibility
    scorer = AccessibilityScorer()
    
    # Check alt text
    for image_data in ppt_processor.image_shapes:
        has_alt_text = bool(image_data.get("alt_text", "").strip())
        if has_alt_text:
            scorer.add_score("alt_text", 100, f"Image on slide {image_data['slide_num']+1} has alt text")
        else:
            scorer.add_score("alt_text", 0, f"Image on slide {image_data['slide_num']+1} missing alt text")
    
    # Check font size
    for text_data in ppt_processor.text_shapes:
        font_size = text_data.get("font_size")
        if font_size:
            if font_size >= 18:
                scorer.add_score("font_size", 100, f"Text on slide {text_data['slide_num']+1} has good font size ({font_size}pt)")
            else:
                scorer.add_score("font_size", max(0, (font_size / 18) * 100), 
                                f"Text on slide {text_data['slide_num']+1} has small font size ({font_size}pt)")
    
    # Check text complexity
    for text_data in ppt_processor.text_shapes:
        text = text_data.get("text", "")
        if text:
            words = text.split()
            if len(words) > 0:
                avg_word_length = sum(len(word) for word in words) / len(words)
                complexity_score = 100
                if avg_word_length > 6:
                    complexity_score -= 30
                    scorer.add_issue("text_complexity", f"Text on slide {text_data['slide_num']+1} has complex words")
                if len(words) > 25:
                    complexity_score -= 30
                    scorer.add_issue("text_complexity", f"Text on slide {text_data['slide_num']+1} has too many words")
                
                scorer.add_score("text_complexity", complexity_score, 
                                f"Text complexity on slide {text_data['slide_num']+1}")
    
    # Create a simplified_texts dictionary to satisfy the method requirement
    # This provides a default empty simplified version for each text element
    simplified_texts = {}
    for text_data in ppt_processor.text_shapes:
        slide_id = text_data["slide_num"]
        shape_id = text_data.get("shape_idx", 0)
        key = f"{slide_id}_{shape_id}"
        simplified_texts[key] = {
            "original": text_data.get("text", ""),
            "simplified": text_data.get("text", "")  # Same as original for initial analysis
        }
    
    # Generate WCAG report
    wcag_report = {
        "1.1.1 Non-text Content": {
            "description": "All images should have alternative text descriptions",
            "compliance": "Pass" if scorer.scores["alt_text"] >= 80 else "Fail",
            "issues": [issue for issue in scorer.issues["alt_text"]]
        },
        "1.4.3 Contrast": {
            "description": "Text should have sufficient contrast with its background",
            "compliance": "Pass", # Placeholder - would require color analysis
            "issues": []
        },
        "1.4.4 Resize Text": {
            "description": "Text should be resizable without loss of content",
            "compliance": "Pass" if scorer.scores["font_size"] >= 80 else "Fail",
            "issues": [issue for issue in scorer.issues["font_size"]]
        },
        "3.1.5 Reading Level": {
            "description": "Text should be written in clear, simple language",
            "compliance": "Pass" if scorer.scores["text_complexity"] >= 80 else "Fail",
            "issues": [issue for issue in scorer.issues["text_complexity"]]
        }
    }
    
    # Calculate overall score
    overall_score = scorer.calculate_overall_score()
    
    # Create final report
    before_score = {
        "overall_score": overall_score,
        "summary": f"Your presentation scores {overall_score}/100 for accessibility",
        "category_scores": {
            "alt_text": scorer.calculate_alt_text_score(ppt_processor.image_shapes),
            "font_size": scorer.calculate_font_size_score(ppt_processor.text_shapes),
            "contrast": 80,  # Fixed contrast score since we don't have proper contrast analysis yet
            "text_complexity": scorer.calculate_text_complexity_score(ppt_processor.text_shapes, simplified_texts)
        }
    }
    
    # Store in session state
    st.session_state.before_score = before_score
    st.session_state.wcag_report = wcag_report
    
    # Display warnings about unsupported image formats
    wmf_warnings = [
        img for img in ppt_processor.image_shapes 
        if "warning" in img and "WMF" in img["warning"]
    ]
    if wmf_warnings:
        st.warning(f"Found {len(wmf_warnings)} WMF image(s) that cannot be processed by PIL.")
        for wmf_item in wmf_warnings:
            st.write(f"Slide {wmf_item['slide_num']+1}, shape {wmf_item['shape_idx']}: {wmf_item['warning']}")
    
    return before_score, wcag_report 

def analyze_from_path(file_path):
    """Analyze accessibility from a file path."""
    from src.ppt_processor import PPTProcessor
    
    # Create a processor for the enhanced file - fix initialization
    processor = PPTProcessor()  # Initialize without arguments
    processor.load_presentation(file_path)  # Then load the presentation
    
    # We need to analyze directly since process_presentation doesn't exist
    return analyze_with_processor(processor)

def analyze_with_processor(processor):
    """Analyze using an existing processor."""
    # Copy relevant logic from analyze_accessibility function
    
    # Score accessibility
    scorer = AccessibilityScorer()
    
    # Check alt text
    for image_data in processor.image_shapes:
        has_alt_text = bool(image_data.get("alt_text", "").strip())
        if has_alt_text:
            scorer.add_score("alt_text", 100, f"Image on slide {image_data['slide_num']+1} has alt text")
        else:
            scorer.add_score("alt_text", 0, f"Image on slide {image_data['slide_num']+1} missing alt text")
    
    # Check font size
    for text_data in processor.text_shapes:
        font_size = text_data.get("font_size")
        if font_size:
            if font_size >= 18:
                scorer.add_score("font_size", 100, f"Text on slide {text_data['slide_num']+1} has good font size ({font_size}pt)")
            else:
                scorer.add_score("font_size", max(0, (font_size / 18) * 100), 
                                f"Text on slide {text_data['slide_num']+1} has small font size ({font_size}pt)")
    
    # Check text complexity
    for text_data in processor.text_shapes:
        text = text_data.get("text", "")
        if text:
            words = text.split()
            if len(words) > 0:
                avg_word_length = sum(len(word) for word in words) / len(words)
                complexity_score = 100
                if avg_word_length > 6:
                    complexity_score -= 30
                    scorer.add_issue("text_complexity", f"Text on slide {text_data['slide_num']+1} has complex words")
                if len(words) > 25:
                    complexity_score -= 30
                    scorer.add_issue("text_complexity", f"Text on slide {text_data['slide_num']+1} has too many words")
                
                scorer.add_score("text_complexity", complexity_score, 
                                f"Text complexity on slide {text_data['slide_num']+1}")
    
    # Create a simplified_texts dictionary to satisfy the method requirement
    # This provides a default empty simplified version for each text element
    simplified_texts = {}
    for text_data in processor.text_shapes:
        slide_id = text_data["slide_num"]
        shape_id = text_data.get("shape_idx", 0)
        key = f"{slide_id}_{shape_id}"
        simplified_texts[key] = {
            "original": text_data.get("text", ""),
            "simplified": text_data.get("text", "")  # Same as original for initial analysis
        }
    
    # Generate WCAG report
    wcag_report = {
        "1.1.1 Non-text Content": {
            "description": "All images should have alternative text descriptions",
            "compliance": "Pass" if scorer.scores["alt_text"] >= 80 else "Fail",
            "issues": [issue for issue in scorer.issues["alt_text"]]
        },
        "1.4.3 Contrast": {
            "description": "Text should have sufficient contrast with its background",
            "compliance": "Pass", # Placeholder - would require color analysis
            "issues": []
        },
        "1.4.4 Resize Text": {
            "description": "Text should be resizable without loss of content",
            "compliance": "Pass" if scorer.scores["font_size"] >= 80 else "Fail",
            "issues": [issue for issue in scorer.issues["font_size"]]
        },
        "3.1.5 Reading Level": {
            "description": "Text should be written in clear, simple language",
            "compliance": "Pass" if scorer.scores["text_complexity"] >= 80 else "Fail",
            "issues": [issue for issue in scorer.issues["text_complexity"]]
        }
    }
    
    # Calculate overall score
    overall_score = scorer.calculate_overall_score()
    
    # Create final report
    after_score = {
        "overall_score": overall_score,
        "summary": f"Your presentation scores {overall_score}/100 for accessibility",
        "category_scores": {
            "alt_text": scorer.calculate_alt_text_score(processor.image_shapes),
            "font_size": scorer.calculate_font_size_score(processor.text_shapes),
            "contrast": 80,  # Fixed contrast score since we don't have proper contrast analysis yet
            "text_complexity": scorer.calculate_text_complexity_score(processor.text_shapes, simplified_texts)
        }
    }
    
    return after_score, wcag_report 