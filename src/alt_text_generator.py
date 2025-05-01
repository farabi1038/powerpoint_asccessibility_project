"""
Alt Text Generator Module using LLaVA via Ollama.

This module handles the generation of alternative text descriptions for images
using the LLaVA (Large Language and Vision Assistant) model via Ollama.
Each distinct component is separated for better modularity.
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
        
    # MODULE 1: Main Alt Text Generation
    def generate_alt_text(self, image_path, detailed=False):
        """Generate alt text for an image"""
        try:
            # Check if the image exists
            if not os.path.exists(image_path):
                return "Image could not be accessed for description"
            
            # Try using Ollama for alt text generation
            if self.check_api_availability():
                prompt_prefix = "Describe this image in detail for someone who cannot see it, focusing on all important visual elements and their significance:" if detailed else "Describe this image concisely:" 
                
                # Read the image
                with open(image_path, "rb") as image_file:
                    image_data = base64.b64encode(image_file.read()).decode('utf-8')
                
                # Prepare the prompt with the image
                prompt = f"{prompt_prefix}\n<img src=\"data:image/jpeg;base64,{image_data}\">"
                
                # Make the API request
                try:
                    response = requests.post(
                        self.api_url,
                        json={
                            "model": self.model,
                            "prompt": prompt,
                            "stream": False,
                            "options": {
                                "num_predict": 500 if detailed else 200
                            }
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        return self._format_alt_text(response.json().get("response", ""), detailed)
                except Exception as e:
                    print(f"Error generating alt text with Ollama: {e}")
                
            # Fallback to placeholder text
            return "Image containing visual content related to the presentation topic"
        except Exception as e:
            print(f"Error generating alt text: {e}")
            return "Image description unavailable"

    # MODULE 2: Image Preparation for API
    def _prepare_image(self, image_path):
        """
        Process and prepare the image for the Ollama API.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Base64-encoded image or None if error
        """
        try:
            # Open the image
            img = Image.open(image_path)
            
            # Convert RGBA to RGB if needed (to fix JPEG conversion issue)
            if img.mode == 'RGBA':
                # Create a white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                # Composite the image with the white background
                background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                img = background
            
            # Resize the image for faster processing
            img = self._resize_image(img)
            
            # Convert image to base64
            buffer = BytesIO()
            img.save(buffer, format="JPEG")  # Always save as JPEG for compatibility
            img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            
            return img_base64
            
        except Exception as e:
            self.logger.error(f"Error preparing image: {str(e)}")
            return None
    
    # MODULE 3: Image Resizing
    def _resize_image(self, img, max_dim=512):
        """
        Resize an image while maintaining aspect ratio.
        
        Args:
            img (PIL.Image): The image to resize
            max_dim (int): Maximum dimension (width or height)
            
        Returns:
            PIL.Image: Resized image
        """
        width, height = img.size
        
        if max(width, height) <= max_dim:
            return img
            
        if width > height:
            new_width = max_dim
            new_height = int(height * (max_dim / width))
        else:
            new_height = max_dim
            new_width = int(width * (max_dim / height))
        
        return img.resize((new_width, new_height), Image.LANCZOS)
    
    # MODULE 4: Ollama API Communication
    def _call_ollama_api(self, img_base64, max_retries=2, timeout=60):
        """
        Call the Ollama API to generate alt text.
        
        Args:
            img_base64 (str): Base64-encoded image
            max_retries (int): Maximum number of retry attempts
            timeout (int): Request timeout in seconds
            
        Returns:
            str: Generated alt text or error message
        """
        # Use a concise prompt to reduce processing time
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
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    alt_text = response.json().get("response", "").strip()
                    
                    # Post-process the response
                    alt_text = self._post_process_text(alt_text)
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
        
        # If all retries failed
        return self.generate_placeholder_text({"slide_num": 0})
    
    # MODULE 5: Text Post-Processing
    def _post_process_text(self, text):
        """
        Post-process the generated alt text.
        
        Args:
            text (str): Raw alt text from the API
            
        Returns:
            str: Processed alt text
        """
        # Remove any leading/trailing whitespace
        text = text.strip()
        
        # Truncate if too long
        if len(text.split()) > 100:
            text = " ".join(text.split()[:50]) + "..."
        
        # Remove any markdown formatting that might have been added
        text = text.replace('*', '').replace('#', '')
        
        # Ensure the text has proper capitalization and punctuation
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
            
        return text

    # MODULE 6: API Availability Check
    def check_api_availability(self):
        """
        Check if the Ollama API is available.
        
        Returns:
            bool: True if API is available, False otherwise
        """
        try:
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
            self.logger.error(f"Error checking Ollama availability: {str(e)}")
            return False
            
    # MODULE 7: Placeholder Text Generation
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

    # MODULE 8: Port Availability Check
    def check_port_availability(self):
        """
        Check if the Ollama port is available.
        
        Returns:
            bool: True if port is free, False if in use
        """
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
            
    # MODULE 9: Batch Processing
    def process_image_batch(self, image_list, slide_indices=None):
        """
        Process a batch of images for alt text generation.
        
        Args:
            image_list (list): List of image paths
            slide_indices (list, optional): List of corresponding slide indices
            
        Returns:
            list: List of generated alt texts
        """
        if slide_indices is None:
            slide_indices = list(range(len(image_list)))
            
        results = []
        
        # Check API availability once for the whole batch
        api_available = self.check_api_availability()
        
        for i, image_path in enumerate(image_list):
            slide_idx = slide_indices[i] if i < len(slide_indices) else i
            
            if api_available and os.path.exists(image_path):
                alt_text = self.generate_alt_text(image_path)
            else:
                alt_text = self.generate_placeholder_text({"slide_num": slide_idx})
                
            results.append(alt_text)
            
        return results 

    def _format_alt_text(self, text, detailed=False):
        """Format and clean the generated alt text"""
        if not text:
            return "Image description unavailable"
        
        # Remove common LLM prefixes
        prefixes_to_remove = [
            "Here's a description of the image:",
            "The image shows",
            "This image shows",
            "This image depicts",
            "In this image,"
        ]
        
        for prefix in prefixes_to_remove:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        
        # Clean up formatting
        text = text.replace("\n", " ").strip()
        
        # Ensure first letter is capitalized
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        # Ensure it ends with a period if it doesn't have ending punctuation
        if text and text[-1] not in ".!?":
            text += "."
        
        # For detailed descriptions, add a prefix if not already descriptive enough
        if detailed and len(text.split()) < 20:
            text = f"Primary slide image showing: {text}"
        
        return text 