"""
Test script for PowerPoint extraction and alt text generation.

This script tests the extraction of content from PowerPoint files
and the generation of alt text using Ollama AI.
"""

import os
import sys
import tempfile
import argparse
from PIL import Image
from src.ppt_processor import PPTProcessor
from src.alt_text_generator import AltTextGenerator

def test_pptx_extraction(pptx_path, verbose=False):
    """
    Test extraction of content from a PowerPoint file.
    
    Args:
        pptx_path (str): Path to the PowerPoint file
        verbose (bool): Whether to print verbose output
        
    Returns:
        tuple: (success, stats, error_message)
    """
    try:
        print(f"Testing extraction from: {pptx_path}")
        
        # Create a processor
        processor = PPTProcessor()
        
        # Load the presentation
        processor.load_presentation(pptx_path)
        
        # Get statistics
        stats = {
            "slides": len(processor.presentation.slides),
            "images": len(processor.image_shapes),
            "text_shapes": len(processor.text_shapes),
            "wmf_images": len([img for img in processor.image_shapes 
                              if 'warning' in img and 'WMF' in img.get('warning', '')])
        }
        
        # Print statistics
        print("\nExtraction Statistics:")
        print(f"- Slides: {stats['slides']}")
        print(f"- Images: {stats['images']}")
        print(f"- Text shapes: {stats['text_shapes']}")
        print(f"- WMF images: {stats['wmf_images']}")
        
        # Print detailed information if verbose
        if verbose:
            print("\nDetailed Information:")
            
            # Print information about images
            print("\nImages:")
            for i, img in enumerate(processor.image_shapes):
                slide_num = img.get("slide_num", 0) + 1
                has_alt = "Yes" if img.get("alt_text") else "No"
                img_path = img.get("image_path", "N/A")
                warnings = img.get("warning", "None")
                
                print(f"  {i+1}. Slide {slide_num} - Has Alt: {has_alt} - Path: {img_path} - Warnings: {warnings}")
            
            # Print information about text shapes
            print("\nText Shapes:")
            for i, txt in enumerate(processor.text_shapes):
                slide_num = txt.get("slide_num", 0) + 1
                font_size = txt.get("font_size", "Unknown")
                text = txt.get("text", "")
                if len(text) > 50:
                    text = text[:47] + "..."
                
                print(f"  {i+1}. Slide {slide_num} - Font Size: {font_size} - Text: {text}")
        
        # Clean up
        processor.cleanup()
        
        return True, stats, None
        
    except Exception as e:
        import traceback
        error_msg = f"Error during extraction: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return False, None, error_msg

def test_alt_text_generation(image_path, verbose=False):
    """
    Test alt text generation for an image using Ollama.
    
    Args:
        image_path (str): Path to the image file
        verbose (bool): Whether to print verbose output
        
    Returns:
        tuple: (success, alt_text, error_message)
    """
    try:
        print(f"Testing alt text generation for: {image_path}")
        
        # Create a generator
        generator = AltTextGenerator()
        
        # Check if Ollama API is available
        api_available = generator.check_api_availability()
        print(f"Ollama API available: {api_available}")
        
        if not api_available:
            return False, None, "Ollama API is not available. Make sure Ollama is running."
        
        # Generate alt text
        print("Generating alt text...")
        alt_text = generator.generate_alt_text(image_path)
        
        print(f"\nGenerated Alt Text: {alt_text}")
        
        return True, alt_text, None
        
    except Exception as e:
        import traceback
        error_msg = f"Error during alt text generation: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return False, None, error_msg

def extract_images_from_pptx(pptx_path, output_dir=None):
    """
    Extract images from a PowerPoint file to disk.
    
    Args:
        pptx_path (str): Path to the PowerPoint file
        output_dir (str): Directory to save images to (optional)
        
    Returns:
        tuple: (success, image_paths, error_message)
    """
    try:
        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        else:
            output_dir = tempfile.mkdtemp()
            
        print(f"Extracting images from {pptx_path} to {output_dir}")
        
        # Create a processor
        processor = PPTProcessor()
        
        # Load the presentation
        processor.load_presentation(pptx_path)
        
        # Extract images
        image_paths = []
        for i, img in enumerate(processor.image_shapes):
            slide_num = img.get("slide_num", 0) + 1
            img_path = img.get("image_path")
            
            if img_path and os.path.exists(img_path):
                # Copy to output directory
                ext = os.path.splitext(img_path)[1]
                output_path = os.path.join(output_dir, f"slide_{slide_num}_image_{i+1}{ext}")
                
                # Copy the file
                with open(img_path, "rb") as src_file:
                    with open(output_path, "wb") as dst_file:
                        dst_file.write(src_file.read())
                        
                image_paths.append(output_path)
                print(f"Extracted image from slide {slide_num} to {output_path}")
        
        # Clean up
        processor.cleanup()
        
        return True, image_paths, None
        
    except Exception as e:
        import traceback
        error_msg = f"Error extracting images: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return False, None, error_msg

def batch_test_alt_text(pptx_path, verbose=False):
    """
    Test batch alt text generation for all images in a PowerPoint file.
    
    Args:
        pptx_path (str): Path to the PowerPoint file
        verbose (bool): Whether to print verbose output
        
    Returns:
        tuple: (success, results, error_message)
    """
    try:
        print(f"Testing batch alt text generation for: {pptx_path}")
        
        # Extract images
        success, image_paths, error = extract_images_from_pptx(pptx_path)
        if not success:
            return False, None, error
            
        if not image_paths:
            return False, None, "No images found in the presentation."
        
        # Create a generator
        generator = AltTextGenerator()
        
        # Check if Ollama API is available
        api_available = generator.check_api_availability()
        print(f"Ollama API available: {api_available}")
        
        if not api_available:
            return False, None, "Ollama API is not available. Make sure Ollama is running."
        
        # Generate alt text for all images in batch
        print(f"Generating alt text for {len(image_paths)} images...")
        alt_texts = generator.process_image_batch(image_paths)
        
        # Print results
        results = []
        for i, (img_path, alt_text) in enumerate(zip(image_paths, alt_texts)):
            results.append({
                "image_path": img_path,
                "alt_text": alt_text
            })
            
            if verbose:
                print(f"\nImage {i+1}: {os.path.basename(img_path)}")
                print(f"Alt Text: {alt_text}")
        
        print(f"\nSuccessfully generated alt text for {len(results)} images.")
        
        return True, results, None
        
    except Exception as e:
        import traceback
        error_msg = f"Error during batch alt text generation: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return False, None, error_msg

def main():
    """Main function to run the tests."""
    parser = argparse.ArgumentParser(description="Test PowerPoint extraction and alt text generation")
    parser.add_argument("--pptx", type=str, help="Path to a PowerPoint file")
    parser.add_argument("--image", type=str, help="Path to an image file")
    parser.add_argument("--extract", action="store_true", help="Extract images from the PowerPoint file")
    parser.add_argument("--batch", action="store_true", help="Test batch alt text generation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print verbose output")
    
    args = parser.parse_args()
    
    if not args.pptx and not args.image:
        print("Error: You must specify either a PowerPoint file (--pptx) or an image file (--image)")
        return 1
    
    if args.pptx:
        # Test extraction
        success, stats, error = test_pptx_extraction(args.pptx, args.verbose)
        
        if not success:
            print("Extraction test failed.")
            return 1
            
        # Extract images if requested
        if args.extract:
            success, image_paths, error = extract_images_from_pptx(
                args.pptx, 
                output_dir="extracted_images"
            )
            
            if not success:
                print("Image extraction failed.")
                return 1
                
            print(f"Successfully extracted {len(image_paths)} images.")
        
        # Test batch alt text generation if requested
        if args.batch:
            success, results, error = batch_test_alt_text(args.pptx, args.verbose)
            
            if not success:
                print("Batch alt text generation failed.")
                return 1
                
            print(f"Successfully generated alt text for {len(results)} images.")
    
    if args.image:
        # Test alt text generation
        success, alt_text, error = test_alt_text_generation(args.image, args.verbose)
        
        if not success:
            print("Alt text generation test failed.")
            return 1
    
    print("All tests completed successfully.")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 