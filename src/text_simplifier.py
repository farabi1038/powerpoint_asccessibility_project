"""
Text Simplification Module

This module simplifies complex text to improve readability.
"""

import ollama
import re

class TextSimplifier:
    def __init__(self, model_name="llava:13b"):
        """Initialize the text simplifier with the specified model"""
        self.model_name = model_name
    
    def simplify_text(self, text):
        """Simplify complex text for better accessibility"""
        if not text or len(text) < 10:
            return text
            
        try:
            # Skip simplification for very simple texts
            words = text.split()
            avg_word_length = sum(len(word) for word in words) / len(words)
            
            if avg_word_length < 5 and len(words) < 20:
                return text
                
            # Prepare prompt for the model
            prompt = f"""
            Rewrite the following text to make it more accessible and easier to understand.
            Use simpler words, shorter sentences, and clearer structure.
            Keep the same meaning but make it more readable.
            
            Text to simplify: {text}
            
            Simplified text:
            """
            
            # Make request to Ollama
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                stream=False
            )
            
            # Process the response
            simplified_text = response['response'].strip()
            
            # Ensure we don't make the text longer
            if len(simplified_text) > len(text) * 1.2:
                simplified_text = self._condense_text(simplified_text)
                
            return simplified_text
            
        except Exception as e:
            print(f"Error simplifying text: {e}")
            return text
    
    def _condense_text(self, text):
        """Condense text to be more concise"""
        # Remove redundant phrases
        redundant_phrases = [
            "it is important to note that",
            "it should be noted that",
            "it is worth mentioning that",
            "as you can see",
            "as shown above"
        ]
        
        for phrase in redundant_phrases:
            text = text.replace(phrase, "")
            
        # Remove excessive spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def batch_simplify_text(self, text_data_list):
        """Simplify multiple text items"""
        results = []
        
        for text_data in text_data_list:
            simplified = self.simplify_text(text_data["text"])
            results.append({
                "slide_num": text_data["slide_num"],
                "shape": text_data["shape"],
                "original_text": text_data["text"],
                "simplified_text": simplified
            })
            
        return results 