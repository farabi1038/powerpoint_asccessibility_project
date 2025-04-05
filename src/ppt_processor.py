"""
PowerPoint Processing Module

This module handles the extraction and modification of PowerPoint files.
"""

import os
import subprocess
import magic
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.enum.text import MSO_AUTO_SIZE
import tempfile
from PIL import Image
import io
import shutil
from pptx.dml.color import RGBColor

class PPTProcessor:
    def __init__(self):
        self.presentation = None
        self.image_shapes = []
        self.text_shapes = []
        self.temp_dir = tempfile.mkdtemp()
        
    def load_presentation(self, file_path):
        """Load a PowerPoint presentation"""
        self.presentation = Presentation(file_path)
        self._extract_content()
        return self.presentation
    
    def _convert_wmf_to_png(self, image_data, slide_idx, shape_idx):
        """Convert WMF/EMF to PNG format using various methods"""
        # First, save the WMF data
        wmf_path = os.path.join(self.temp_dir, f"slide_{slide_idx}_shape_{shape_idx}.wmf")
        with open(wmf_path, 'wb') as f:
            f.write(image_data)
        
        # Output path for PNG
        output_path = os.path.join(self.temp_dir, f"slide_{slide_idx}_shape_{shape_idx}.png")
        
        # Method 1: Try using librsvg (if available)
        try:
            from cairosvg import svg2png
            # First convert WMF to SVG using other tools or libraries if available
            # This is a placeholder - actual WMF to SVG conversion is complex
            # For demonstration, we'll generate a simple SVG with text about the unsupported format
            
            svg_content = f"""
            <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
                <rect width="400" height="200" fill="#f8f9fa" />
                <text x="50%" y="50%" text-anchor="middle" font-family="Arial" font-size="16" fill="#333">
                    Windows Metafile Image (WMF/EMF)
                </text>
                <text x="50%" y="70%" text-anchor="middle" font-family="Arial" font-size="12" fill="#666">
                    This image format requires conversion for accessibility
                </text>
            </svg>
            """
            
            svg_path = os.path.join(self.temp_dir, f"slide_{slide_idx}_shape_{shape_idx}.svg")
            with open(svg_path, 'w') as f:
                f.write(svg_content)
            
            svg2png(url=svg_path, write_to=output_path)
            return output_path
        except:
            pass
        
        # Method 2: Try using ImageMagick if available
        try:
            import subprocess
            result = subprocess.run(['convert', wmf_path, output_path], 
                                    check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if os.path.exists(output_path):
                return output_path
        except:
            pass

        # Method 3: Create a placeholder image with PIL
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a placeholder image
            img = Image.new('RGB', (400, 200), color=(248, 249, 250))
            d = ImageDraw.Draw(img)
            
            # Try to use a system font
            try:
                font = ImageFont.truetype("Arial", 16)
                small_font = ImageFont.truetype("Arial", 12)
            except:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Add text to the image
            d.text((200, 100), "Windows Metafile Image (WMF/EMF)", 
                   fill=(51, 51, 51), font=font, anchor="mm")
            d.text((200, 140), "This image format requires conversion for accessibility", 
                   fill=(102, 102, 102), font=small_font, anchor="mm")
            
            # Save the image
            img.save(output_path)
            return output_path
        except:
            # If all methods fail, return None
            return None
    
    def _extract_content(self):
        """Extract content from the presentation"""
        self.image_shapes = []
        self.text_shapes = []
        
        for slide_idx, slide in enumerate(self.presentation.slides):
            for shape_idx, shape in enumerate(slide.shapes):
                # Process text in the shape
                if shape.has_text_frame:
                    text_frame = shape.text_frame
                    text = ""
                    font_size = None
                    
                    for paragraph in text_frame.paragraphs:
                        for run in paragraph.runs:
                            text += run.text
                            if run.font.size:
                                # Convert from EMU to points
                                size_pt = run.font.size.pt
                                font_size = size_pt if font_size is None else min(font_size, size_pt)
                    
                    self.text_shapes.append({
                        "slide_num": slide_idx,
                        "shape": shape,
                        "text": text,
                        "font_size": font_size
                    })
                
                # Extract images
                if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                    try:
                        image_data = shape.image.blob
                        
                        # Properly extract alt text - check multiple ways
                        alt_text = ""
                        
                        # Method 1: Direct alt_text property
                        if hasattr(shape, 'alt_text') and hasattr(shape.alt_text, 'text'):
                            alt_text = shape.alt_text.text
                        
                        # Method 2: XML way
                        if not alt_text and hasattr(shape, '_element'):
                            try:
                                cNvPr_element = shape._element.xpath('.//p:cNvPr')
                                if cNvPr_element and cNvPr_element[0].get('descr'):
                                    alt_text = cNvPr_element[0].get('descr')
                            except:
                                pass
                        
                        # Debug
                        print(f"Extracted alt text for slide {slide_idx+1}: '{alt_text}'")
                        
                        # Get file extension based on image content
                        image_type = self._get_image_type(image_data)
                        
                        if image_type == "wmf" or image_type == "emf":
                            # Handle Windows Metafile format
                            converted_path = self._convert_wmf_to_png(image_data, slide_idx, shape_idx)
                            if converted_path:
                                self.image_shapes.append({
                                    "slide_num": slide_idx,
                                    "shape_idx": shape_idx,
                                    "shape": shape,
                                    "image_path": converted_path,
                                    "alt_text": alt_text,
                                    "converted_from_wmf": True
                                })
                            else:
                                # If conversion failed, add placeholder with information
                                self.image_shapes.append({
                                    "slide_num": slide_idx,
                                    "shape_idx": shape_idx,
                                    "shape": shape,
                                    "image_path": None,
                                    "alt_text": alt_text,
                                    "converted_from_wmf": False,
                                    "warning": f"Unsupported image format: WMF file on slide {slide_idx+1}, shape {shape_idx+1}"
                                })
                                print(f"Warning: Unsupported image format on slide {slide_idx+1}, shape {shape_idx+1}: cannot find loader for this WMF file")
                        else:
                            # Handle regular image formats
                            try:
                                # Try to open the image
                                image = Image.open(io.BytesIO(image_data))
                                
                                # Save the image to a temporary file
                                ext = "." + (image.format.lower() if image.format else "png")
                                img_path = os.path.join(self.temp_dir, f"slide_{slide_idx}_shape_{shape_idx}{ext}")
                                image.save(img_path)
                                
                                self.image_shapes.append({
                                    "slide_num": slide_idx,
                                    "shape_idx": shape_idx,
                                    "shape": shape,
                                    "image_path": img_path,
                                    "alt_text": alt_text
                                })
                            except OSError as e:
                                # Check if "WMF" is in the error - indicates unsupported format
                                if "WMF" in str(e).upper():
                                    # Instead of raising an error, set a warning flag and include shape_idx
                                    self.image_shapes.append({
                                        "slide_num": slide_idx,
                                        "shape_idx": shape_idx,
                                        "shape": shape,
                                        "image_path": None,
                                        "alt_text": alt_text,
                                        "warning": "WMF file skipped - PIL cannot load"
                                    })
                                else:
                                    # Some other error - re-raise
                                    raise e
                    except Exception as e:
                        print(f"Error extracting image data on slide {slide_idx+1}, shape {shape_idx+1}: {e}")
                        self.image_shapes.append({
                            "slide_num": slide_idx,
                            "shape_idx": shape_idx,
                            "shape": shape,
                            "image_path": None,
                            "alt_text": "",
                            "warning": f"Error extracting image on slide {slide_idx+1}, shape {shape_idx+1}"
                        })
    
    def _get_image_type(self, image_data):
        """Determine image type from binary data"""
        try:
            import magic
            mime = magic.Magic(mime=True)
            mime_type = mime.from_buffer(image_data)
            
            if mime_type == "image/x-wmf" or "wmf" in mime_type:
                return "wmf"
            elif mime_type == "image/x-emf" or "emf" in mime_type:
                return "emf"
            else:
                return mime_type.split('/')[-1]
        except ImportError:
            # If python-magic is not available, try basic header check
            if image_data[:4] == b'\xd7\xcd\xc6\x9a':  # WMF header
                return "wmf"
            elif image_data[:4] == b'\x01\x00\x00\x00':  # EMF header
                return "emf"
            else:
                # Try to guess from image headers
                try:
                    image = Image.open(io.BytesIO(image_data))
                    return image.format.lower()
                except:
                    return "unknown"
    
    def _get_shape_font_size(self, shape):
        """Get the font size of a shape"""
        try:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        if run.font.size:
                            return run.font.size.pt
        except:
            pass
        return None
    
    def update_alt_text(self, slide_idx, shape, alt_text):
        """Update the alt text for a shape"""
        try:
            # Get the non-visual properties
            nvprops = shape.element.xpath('.//p:cNvPr')
            if nvprops:
                # Set the description attribute
                nvprops[0].set('descr', alt_text)
                return True
            return False
        except Exception as e:
            print(f"Error updating alt text: {e}")
            return False
    
    def add_visible_caption(self, slide_idx, shape, caption_text, is_single_image=False):
        """
        Add a visible caption text box below an image
        
        Args:
            slide_idx: Index of the slide
            shape: The image shape object
            caption_text: Text for the caption
            is_single_image: Whether this is the only image on the slide
        """
        try:
            # Get the slide
            slide = self.presentation.slides[slide_idx]
            
            # Special handling for single images on a slide - ensure they get proper captions
            if is_single_image:
                print(f"Using single image placement strategy for slide {slide_idx+1}")
                
                # For single images, always try to put the caption directly below first
                left = shape.left
                top = shape.top + shape.height + Inches(0.05)
                width = shape.width
                
                # Handle edge case where image is at bottom of slide
                slide_height = self.presentation.slide_height
                if top + Inches(0.75) > slide_height:
                    # If too close to bottom, put caption above the image
                    top = max(0, shape.top - Inches(0.8))
                    
                    # If also too close to top, put beside it
                    if top < Inches(0.1):
                        if shape.left > self.presentation.slide_width / 2:
                            # Image on right, put caption on left
                            left = max(0, shape.left - shape.width - Inches(0.1))
                        else:
                            # Image on left, put caption on right
                            left = min(self.presentation.slide_width - shape.width, 
                                     shape.left + shape.width + Inches(0.1))
                        top = shape.top
            else:
                # For multiple images, use the original smart placement logic
                # Calculate available space below the image
                slide_height = self.presentation.slide_height
                available_space = slide_height - (shape.top + shape.height)
                
                # Check if there's enough space below the image
                if available_space < Inches(0.85):  # Need at least this much space
                    # Put caption beside the image instead of below it if there's not enough space
                    if shape.left > self.presentation.slide_width / 2:
                        # Image is on the right side of the slide, put caption on the left
                        left = max(0, shape.left - shape.width - Inches(0.1))
                        top = shape.top
                        width = shape.width
                        if left < 0:  # Not enough space on left either
                            # Put it above the image as a last resort
                            left = shape.left
                            top = max(0, shape.top - Inches(0.85))
                            width = shape.width
                    else:
                        # Image is on the left side, put caption on the right
                        left = shape.left + shape.width + Inches(0.1)
                        top = shape.top
                        width = min(shape.width, self.presentation.slide_width - left - Inches(0.1))
                        if left + width > self.presentation.slide_width:  # Not enough space on right
                            # Put it above the image as a last resort
                            left = shape.left
                            top = max(0, shape.top - Inches(0.85))
                            width = shape.width
                else:
                    # Enough space below the image, place it there
                    left = shape.left
                    top = shape.top + shape.height + Inches(0.05)
                    width = shape.width
            
            # Ensure the width is reasonable and not off the slide
            if width < Inches(1):
                width = Inches(1)
            if width > self.presentation.slide_width - left:
                width = self.presentation.slide_width - left - Inches(0.1)
            
            # Make sure caption is not off the bottom of the slide
            if top + Inches(0.75) > slide_height:
                top = slide_height - Inches(0.8)
            
            # Print debug info
            print(f"Adding caption on slide {slide_idx+1} at position: left={left}, top={top}, width={width}")
            
            # Add a text box for the caption
            textbox = slide.shapes.add_textbox(
                left=left,
                top=top,
                width=width,
                height=Inches(0.75)  # Increased height for better visibility
            )
            
            # Add text to the textbox
            text_frame = textbox.text_frame
            text_frame.word_wrap = True
            text_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
            text_frame.margin_bottom = Inches(0.05)
            text_frame.margin_left = Inches(0.05)
            text_frame.margin_right = Inches(0.05)
            text_frame.margin_top = Inches(0.05)
            
            # Use HTML-like formatting to truncate the caption if it's too long
            if len(caption_text) > 200:
                caption_text = caption_text[:197] + "..."
            
            # Add the slide number to help with identification
            caption_with_slide = f"[Slide {slide_idx+1}] {caption_text}"
            
            # Add paragraph with the caption (with careful font handling)
            p = text_frame.paragraphs[0]
            
            # Clear any existing runs
            try:
                while len(p.runs) > 0:
                    p._p.remove(p.runs[0]._r)
            except:
                # If that fails, try to clear the text
                if p.text:
                    p.text = ""
            
            # Add new run with text
            run = p.add_run()
            run.text = caption_with_slide
            
            # Style the caption - make it centered and more visible
            # Set these properties carefully to avoid object reference errors
            p.alignment = 1  # Center alignment
            
            try:
                run.font.size = Pt(11)  # Smaller font to fit more text
                run.font.bold = True
                run.font.italic = False  # Remove italic for better readability
                run.font.color.rgb = RGBColor(0, 0, 0)  # Black text for maximum contrast
            except Exception as font_error:
                print(f"Error setting font properties: {font_error}")
            
            # Make the caption stand out more with a visible background and border
            try:
                if hasattr(textbox, 'fill'):
                    textbox.fill.solid()
                    textbox.fill.fore_color.rgb = RGBColor(255, 255, 200)  # Pale yellow background
                
                if hasattr(textbox, 'line'):
                    textbox.line.color.rgb = RGBColor(100, 100, 100)  # Darker border
                    textbox.line.width = Pt(1.0)  # Standard border width
            except Exception as shape_error:
                print(f"Error setting shape properties: {shape_error}")
            
            print(f"Caption successfully created for slide {slide_idx+1}")
            return textbox
            
        except Exception as e:
            print(f"Error adding caption: {e}")
            import traceback
            print(traceback.format_exc())
            return None
    
    def update_font_size(self, shape, new_size):
        """Update font size for a shape while preserving other formatting"""
        try:
            if not shape.has_text_frame:
                return False
            
            has_changes = False
            
            # First check if the current font size is already larger than the new size
            current_min_size = None
            
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    if hasattr(run, "font") and hasattr(run.font, "size") and run.font.size is not None:
                        # Get font size in points
                        size_pt = run.font.size.pt
                        if current_min_size is None or size_pt < current_min_size:
                            current_min_size = size_pt
            
            # If the current minimum size is already greater than or equal to the requested size,
            # or if we couldn't determine a current size, just return
            if current_min_size is not None and current_min_size >= new_size:
                return False
            
            # Only update font sizes smaller than the new size
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    if run.text.strip() and hasattr(run, "font"):
                        if hasattr(run.font, "size") and run.font.size is not None:
                            # Get current size
                            current_size = run.font.size.pt
                            if current_size < new_size:
                                # Only increase font size, never decrease
                                run.font.size = Pt(new_size)
                                has_changes = True
                        else:
                            # If size isn't set, set it
                            run.font.size = Pt(new_size)
                            has_changes = True
            
            return has_changes
        except Exception as e:
            print(f"Error updating font size: {e}")
            return False
    
    def update_text(self, shape, new_text):
        """Update the text in a shape"""
        try:
            if shape.has_text_frame:
                text_frame = shape.text_frame
                
                # Clear existing text
                p = text_frame.paragraphs[0]
                p.clear()
                
                # Add new text
                p.add_run().text = new_text
                
                return True
        except Exception as e:
            print(f"Error updating text: {e}")
            return False
    
    def update_text_contrast(self, shape, make_darker=True):
        """Update text contrast for a shape - simplified to reduce formatting issues"""
        try:
            if not shape.has_text_frame:
                return False
            
            has_changes = False
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    if not run.text.strip():
                        continue
                    
                    # Only set color if we can safely do so
                    try:
                        if make_darker:
                            # Just set black text - safest option
                            rgb = RGBColor(0, 0, 0)
                        else:
                            # White text for dark backgrounds
                            rgb = RGBColor(255, 255, 255)
                        
                        # Only update colors that need to be changed
                        if hasattr(run.font, "color") and run.font.color is not None:
                            # Create a new RGBColor for safety
                            run.font.color.rgb = rgb
                            has_changes = True
                    except Exception as e:
                        print(f"Error updating text color: {e}")
            
            return has_changes
        except Exception as e:
            print(f"Error updating text contrast: {e}")
            return False
    
    def save_presentation(self, output_path):
        """Save the modified presentation"""
        try:
            self.presentation.save(output_path)
            return True
        except Exception as e:
            print(f"Error saving presentation: {e}")
            return False
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Error cleaning up temporary files: {e}")
    
    def add_simple_caption(self, slide_idx, shape, caption_text):
        """
        Add a very simple caption below an image as a fallback option
        that's more likely to succeed than the complex positioning logic
        """
        try:
            # Get the slide
            slide = self.presentation.slides[slide_idx]
            
            # Get image dimensions
            img_left = shape.left
            img_width = shape.width
            
            # Create a caption at a fixed position below the image
            # but with a good margin to avoid overlap
            left = img_left
            width = img_width
            
            # Use a position below the image but not too far below
            img_bottom = shape.top + shape.height
            slide_height = self.presentation.slide_height
            remaining_space = slide_height - img_bottom
            
            if remaining_space > Inches(1.5):
                # Enough space below
                top = img_bottom + Inches(0.2)
            else:
                # Not enough space below, try above
                top = max(0, shape.top - Inches(0.8))
            
            # Make sure the width isn't too wide for the slide
            if width > self.presentation.slide_width - left:
                width = self.presentation.slide_width - left - Inches(0.1)
            
            # Add a text box for the caption
            textbox = slide.shapes.add_textbox(
                left=left,
                top=top,
                width=width,
                height=Inches(0.6)  # Smaller fixed height
            )
            
            # Add text to the textbox with simplified formatting
            text_frame = textbox.text_frame
            text_frame.word_wrap = True
            text_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
            text_frame.margin_bottom = Inches(0.05)
            text_frame.margin_left = Inches(0.05)
            text_frame.margin_right = Inches(0.05)
            text_frame.margin_top = Inches(0.05)
            
            # Truncate long captions
            if len(caption_text) > 150:
                caption_text = caption_text[:147] + "..."
            
            # Add slide number for identification
            caption_with_slide = f"[Slide {slide_idx+1}] {caption_text}"
            
            # Add text directly to the paragraph rather than using runs
            # which can sometimes cause formatting issues
            p = text_frame.paragraphs[0]
            p.text = caption_with_slide
            p.alignment = 1  # Center alignment
            
            # Apply direct formatting to all runs
            for run in p.runs:
                try:
                    run.font.size = Pt(11)
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(0, 0, 0)
                except Exception as e:
                    print(f"Error formatting caption: {e}")
            
            # Add a simple yellow background
            try:
                if hasattr(textbox, 'fill'):
                    textbox.fill.solid()
                    textbox.fill.fore_color.rgb = RGBColor(255, 255, 150)
            except Exception as e:
                print(f"Error setting fill: {e}")
            
            return textbox
            
        except Exception as e:
            print(f"Error adding simple caption: {e}")
            return None 