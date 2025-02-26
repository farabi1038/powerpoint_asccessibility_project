"""
Accessibility Checker Module

This module checks and fixes font and contrast accessibility issues.
"""

import wcag_contrast_ratio as contrast
from PIL import Image, ImageStat
import numpy as np
from pptx.dml.color import RGBColor
from pptx.util import Pt

class AccessibilityChecker:
    def __init__(self):
        # WCAG AA requires a minimum contrast ratio of 4.5:1 for normal text
        # and 3:1 for large text (18pt or 14pt bold)
        self.min_contrast_ratio = 4.5
        self.min_large_text_contrast_ratio = 3.0
        
        # Minimum font size recommendations (points)
        self.min_font_size = 18.0  # Minimum recommended size
    
    def check_font_size(self, font_size):
        """Check if font size meets accessibility standards"""
        if font_size is None:
            return False, "Unknown font size"
        
        if font_size < self.min_font_size:
            return False, f"Font size {font_size}pt is too small (min: {self.min_font_size}pt)"
            
        return True, f"Font size {font_size}pt is acceptable"
    
    def get_background_color(self, image_path, x, y, width, height):
        """Estimate the background color of a text region in an image"""
        try:
            with Image.open(image_path) as img:
                # Extract the region
                region = img.crop((x, y, x + width, y + height))
                # Get average color
                stat = ImageStat.Stat(region)
                avg_color = tuple(int(round(c)) for c in stat.mean)
                return avg_color
        except:
            # Default to white if we can't determine
            return (255, 255, 255)
    
    def check_contrast(self, text_color, background_color, is_large_text=False):
        """Check if text and background colors have sufficient contrast"""
        # Convert colors to the format expected by wcag_contrast_ratio
        text_color_hex = '#{:02x}{:02x}{:02x}'.format(*text_color)
        bg_color_hex = '#{:02x}{:02x}{:02x}'.format(*background_color)
        
        # Calculate contrast ratio
        ratio = contrast.rgb(text_color_hex, bg_color_hex)
        
        min_ratio = self.min_large_text_contrast_ratio if is_large_text else self.min_contrast_ratio
        
        if ratio < min_ratio:
            return False, f"Contrast ratio {ratio:.2f}:1 is below the required {min_ratio}:1"
            
        return True, f"Contrast ratio {ratio:.2f}:1 meets standards"
    
    def suggest_font_size(self, current_size):
        """Suggest an appropriate font size"""
        if current_size is None:
            return self.min_font_size
        
        if current_size < self.min_font_size:
            return self.min_font_size
            
        return current_size
    
    def suggest_contrast_fix(self, text_color, background_color, is_large_text=False):
        """Suggest fixes for contrast issues"""
        # This is a simple implementation that darkens text or lightens background
        text_rgb = list(text_color)
        bg_rgb = list(background_color)
        
        # Calculate luminance to decide if text should be darkened or background lightened
        text_lum = 0.299 * text_rgb[0] + 0.587 * text_rgb[1] + 0.114 * text_rgb[2]
        bg_lum = 0.299 * bg_rgb[0] + 0.587 * bg_rgb[1] + 0.114 * bg_rgb[2]
        
        # If the text is already dark, lighten the background
        if text_lum < 128:
            # Make background lighter
            bg_rgb = [min(255, c + 50) for c in bg_rgb]
        else:
            # Make text darker
            text_rgb = [max(0, c - 50) for c in text_rgb]
        
        return tuple(text_rgb), tuple(bg_rgb)
    
    def get_pptx_rgb_color(self, rgb_tuple):
        """Convert RGB tuple to PowerPoint RGBColor"""
        r, g, b = rgb_tuple
        return RGBColor(r, g, b) 