"""
Alt Text Generator Module using LLaVA via Ollama.

This module handles the generation of alternative text descriptions for images
using the LLaVA (Large Language and Vision Assistant) model via Ollama.
"""

import requests
import base64
import os
import time
from PIL import Image
from io import BytesIO
import logging
import socket

class AltTextGenerator:
    """
    Generates alt text for images using LLaVA model via Ollama.
    """
    
    def __init__(self, model="llava:latest", api_url="http://localhost:11434/api/generate"):
        """
        Initialize the alt text generator.
        
        Args:
            model (str): The model name to use in Ollama
            api_url (str): The Ollama API endpoint
        """
        self.model = model
        self.api_url = api_url
        self.logger = logging.getLogger(__name__)
        
    def generate_alt_text(self, image_path, max_retries=2, timeout=60):
        """
        Generate alternative text for an image using LLaVA model.
        
        Args:
            image_path (str): Path to the image file
            max_retries (int): Maximum number of retry attempts
            timeout (int): Request timeout in seconds
            
        Returns:
            str: Generated alt text or error message
        """
        if not os.path.exists(image_path):
            return "Image not found"
        
        try:
            # Resize image to reduce payload size if necessary
            img = Image.open(image_path)
            
            # Convert RGBA to RGB if needed (to fix JPEG conversion issue)
            if img.mode == 'RGBA':
                # Create a white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                # Composite the image with the white background
                background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                img = background
            
            # Further reduce image size for faster processing
            max_dim = 512  # Reduce max dimension to reduce timeout issues
            
            if max(img.size) > max_dim:
                width, height = img.size
                if width > height:
                    new_width = max_dim
                    new_height = int(height * (max_dim / width))
                else:
                    new_height = max_dim
                    new_width = int(width * (max_dim / height))
                
                img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Convert image to base64
            buffer = BytesIO()
            img.save(buffer, format="JPEG")  # Always save as JPEG for compatibility
            img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            
            # Use a more concise prompt to reduce processing time
            prompt = (
                "Briefly describe this image for a visually impaired person. "
                "Focus only on key elements. Keep it under 50 words."
            )
            
            # Call Ollama API with retries
            retries = 0
            while retries <= max_retries:
                try:
                    response = requests.post(
                        self.api_url,
                        json={
                            "model": self.model,
                            "prompt": prompt,
                            "images": [img_base64],
                            "stream": False,
                            "options": {
                                "temperature": 0.1,  # Lower temperature for more focused responses
                                "num_predict": 100   # Limit token generation
                            }
                        },
                        timeout=timeout  # Increased timeout
                    )
                    
                    if response.status_code == 200:
                        alt_text = response.json().get("response", "").strip()
                        
                        # Post-process to make it more concise if needed
                        if len(alt_text.split()) > 100:
                            alt_text = " ".join(alt_text.split()[:50]) + "..."
                            
                        return alt_text
                    else:
                        self.logger.error(f"API error: {response.status_code}, {response.text}")
                        retries += 1
                        if retries <= max_retries:
                            time.sleep(2)  # Wait before retrying
                        
                except requests.RequestException as e:
                    self.logger.error(f"Request failed: {str(e)}")
                    retries += 1
                    if retries <= max_retries:
                        time.sleep(2)  # Wait before retrying
                    # If it's the last retry and still failing, use placeholder
                    if retries > max_retries:
                        return self.generate_placeholder_text({"slide_num": 0})
            
            return "Image description unavailable (API error)"
                
        except Exception as e:
            self.logger.error(f"Alt text generation error: {str(e)}")
            # Return a placeholder on error
            return self.generate_placeholder_text({"slide_num": 0})

    def check_api_availability(self):
        """Check if the Ollama API is available"""
        import logging
        
        try:
            import requests
            # Try different Ollama API endpoints
            endpoints = [
                "http://localhost:11434/api/health", 
                "http://localhost:11434/api/version",
                "http://localhost:11434/api",
                "http://localhost:11434/"
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, timeout=5)
                    if response.status_code < 500:  # Accept any non-server error response
                        return True
                except:
                    continue
                
            # If we got here, none of the endpoints worked
            return False
        except Exception as e:
            logging.error(f"Error checking Ollama availability: {str(e)}")
            return False
            
    def generate_placeholder_text(self, image_info):
        """
        Generate placeholder alt text when API is not available.
        
        Args:
            image_info (dict): Information about the image
            
        Returns:
            str: Basic placeholder text
        """
        slide_num = image_info.get("slide_num", 0) + 1
        return f"Image on slide {slide_num} (AI description not available)"

    def check_port_availability(self):
        """Check if the Ollama port is available or in use by another service"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("localhost", 11434))
            # If we get here, the port is free
            s.close()
            return True
        except:
            # Port is in use
            s.close()
            return False 