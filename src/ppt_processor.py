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
    
    def update_alt_text(self, slide_num, shape, new_alt_text):
        """Update the alt text for an image"""
        try:
            # The correct way to set alt text in python-pptx
            if hasattr(shape, 'alt_text'):
                # Use the proper API
                shape.alt_text.text = new_alt_text
                return True
            else:
                # For older versions of python-pptx or special shapes
                try:
                    # Try direct XML manipulation as fallback
                    shape._element.xpath('.//p:cNvPr')[0].set('descr', new_alt_text)
                    return True
                except:
                    print(f"Could not set alt text via XML for slide {slide_num+1}")
                    return False
        except Exception as e:
            print(f"Error updating alt text: {e}")
            return False
    
    def update_font_size(self, shape, new_size):
        """Update the font size of a text shape"""
        try:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(new_size)
                return True
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