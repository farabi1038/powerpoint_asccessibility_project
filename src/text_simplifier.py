"""
Text Simplification Module

This module simplifies complex text to improve readability.
"""

import requests
import re

class TextSimplifier:
    def __init__(self, model_name="llama3", api_url="http://localhost:11434/api/generate"):
        """Initialize the text simplifier with the specified model"""
        self.model_name = model_name
        self.api_url = api_url
    
    def is_text_complex(self, text):
        """Determine if text is complex and needs simplification"""
        if not text or len(text) < 15:
            return False
            
        # Check complexity based on word length and sentence length
        words = text.split()
        if len(words) < 15:  # Short texts aren't complex
            return False
            
        # Calculate average word length
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Calculate sentence length
        sentences = re.split(r'[.!?]+', text)
        avg_sentence_length = len(words) / max(1, len([s for s in sentences if s.strip()]))
        
        # Text is complex if average word length is high or sentences are long
        return (avg_word_length > 6) or (avg_sentence_length > 20)
    
    def basic_simplify(self, text):
        """Perform basic text simplification without using API"""
        if not text or len(text) < 15:
            return text
            
        # Replace complex words with simpler alternatives
        replacements = {
            "utilize": "use",
            "implementation": "use",
            "facilitate": "help",
            "consequently": "so",
            "subsequently": "then",
            "additionally": "also",
            "furthermore": "also",
            "demonstrate": "show",
            "modification": "change",
            "sufficient": "enough",
            "requirement": "need",
            "prioritize": "focus on",
            "fundamental": "basic",
            "endeavor": "try"
        }
        
        result = text
        for complex_word, simple_word in replacements.items():
            result = re.sub(r'\b' + complex_word + r'\b', simple_word, result, flags=re.IGNORECASE)
            
        # Split very long sentences
        sentences = re.split(r'([.!?])', text)
        simplified_sentences = []
        
        for i in range(0, len(sentences), 2):
            if i+1 < len(sentences):
                sentence = sentences[i] + sentences[i+1]
            else:
                sentence = sentences[i]
                
            # If sentence is very long, try to split it
            if len(sentence.split()) > 25:
                # Split on conjunctions or commas
                parts = re.split(r',\s*|\s+and\s+|\s+but\s+|\s+or\s+|\s+so\s+|\s+because\s+', sentence)
                parts = [p for p in parts if p.strip()]
                
                if len(parts) > 1:
                    # Recombine with proper punctuation
                    sentence = ". ".join(p.strip().capitalize() for p in parts if p.strip())
            
            if sentence.strip():
                simplified_sentences.append(sentence)
                
        result = " ".join(simplified_sentences)
        
        return result.strip()
        
    def simplify_text(self, text, max_retries=2):
        """Simplify complex text for better accessibility"""
        if not text or len(text) < 10:
            return text
            
        try:
            # Skip simplification for very simple texts
            words = text.split()
            if not words:
                return text
                
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
            
            # Make request to Ollama API
            for attempt in range(max_retries + 1):
                try:
                    response = requests.post(
                        self.api_url,
                        json={
                            "model": self.model_name,
                            "prompt": prompt,
                            "stream": False,
                            "options": {
                                "temperature": 0.1,
                                "num_predict": 100
                            }
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        simplified_text = response.json().get("response", "").strip()
                        
                        # Ensure we don't make the text longer
                        if len(simplified_text) > len(text) * 1.2:
                            simplified_text = self._condense_text(simplified_text)
                            
                        return simplified_text
                except Exception as e:
                    if attempt < max_retries:
                        print(f"Retry {attempt+1} after error: {e}")
                        continue
            
            # If all retries failed, return original
            return text
            
        except Exception as e:
            print(f"Error simplifying text: {e}")
            return text
    
    def check_api_availability(self):
        """Check if the Ollama API is available"""
        try:
            response = requests.get("http://localhost:11434/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False
            
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
        results = {}
        
        for text_data in text_data_list:
            key = f"{text_data['slide_num']}_{text_data.get('shape_idx', 0)}"
            
            # Only simplify complex text
            text = text_data.get("text", "")
            words = text.split()
            complex_text = False
            
            if words:
                avg_word_length = sum(len(word) for word in words) / len(words)
                if avg_word_length > 6 or len(words) > 25:
                    complex_text = True
            
            if complex_text:
                simplified = self.simplify_text(text)
            else:
                simplified = text  # No need to simplify
            
            results[key] = {
                "original": text,
                "simplified": simplified
            }
            
        return results 