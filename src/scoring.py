"""
Accessibility Scoring Module

This module implements an accessibility scoring system similar to Canvas Ally.
"""

class AccessibilityScorer:
    def __init__(self):
        # Define scoring criteria weights
        self.weights = {
            "alt_text": 0.3,
            "font_size": 0.25,
            "contrast": 0.25,
            "text_complexity": 0.2
        }
        
        # Track individual scores
        self.scores = {
            "alt_text": 0,
            "font_size": 0,
            "contrast": 0,
            "text_complexity": 0
        }
        
        # Track issues
        self.issues = {
            "alt_text": [],
            "font_size": [],
            "contrast": [],
            "text_complexity": []
        }
        
        # Track evaluated items
        self.evaluated_items = {
            "alt_text": 0,
            "font_size": 0,
            "contrast": 0,
            "text_complexity": 0
        }
    
    def calculate_alt_text_score(self, image_shapes):
        """Calculate score for alt text"""
        if not image_shapes:
            self.scores["alt_text"] = 100
            return 100
            
        missing_alt = 0
        poor_alt = 0
        
        for img in image_shapes:
            alt = img.get("alt_text", "")
            
            # Debug the alt text being checked
            print(f"Scoring alt text for image: '{alt}'")
            
            if not alt or alt.strip() == "":
                missing_alt += 1
                self.issues["alt_text"].append(f"Slide {img['slide_num']+1}: Missing alt text")
            elif len(alt) < 10:
                poor_alt += 1
                self.issues["alt_text"].append(f"Slide {img['slide_num']+1}: Alt text too short")
        
        total = len(image_shapes)
        score = 100 - (missing_alt * 100 / total) - (poor_alt * 30 / total)
        score = max(0, min(100, score))
        
        # Debug the calculated score
        print(f"Alt text score calculation: total={total}, missing={missing_alt}, poor={poor_alt}, score={score}")
        
        self.scores["alt_text"] = score
        return score
    
    def calculate_font_size_score(self, text_shapes):
        """Calculate score for font size"""
        if not text_shapes:
            self.scores["font_size"] = 100
            return 100
            
        small_fonts = 0
        
        for text in text_shapes:
            font_size = text.get("font_size")
            
            if font_size is None:
                continue
                
            if font_size < 18:
                small_fonts += 1
                self.issues["font_size"].append(f"Slide {text['slide_num']+1}: Font size {font_size}pt is too small")
        
        total = len(text_shapes)
        score = 100 - (small_fonts * 100 / total)
        score = max(0, min(100, score))
        
        self.scores["font_size"] = score
        return score
    
    def calculate_contrast_score(self, contrast_issues):
        """Calculate score for contrast"""
        if not contrast_issues:
            self.scores["contrast"] = 100
            return 100
            
        self.issues["contrast"] = contrast_issues
        score = 100 - (len(contrast_issues) * 20)
        score = max(0, min(100, score))
        
        self.scores["contrast"] = score
        return score
    
    def calculate_text_complexity_score(self, original_texts, simplified_texts):
        """Calculate score for text complexity"""
        if not original_texts:
            self.scores["text_complexity"] = 100
            return 100
            
        complex_texts = 0
        
        for i, (orig, simp) in enumerate(zip(original_texts, simplified_texts)):
            # If the simplified text is significantly different, consider the original complex
            if len(orig) > 100 and self._text_difference_ratio(orig, simp) > 0.3:
                complex_texts += 1
                self.issues["text_complexity"].append(f"Slide {i+1}: Text is too complex")
        
        total = len(original_texts)
        score = 100 - (complex_texts * 100 / total)
        score = max(0, min(100, score))
        
        self.scores["text_complexity"] = score
        return score
    
    def _text_difference_ratio(self, text1, text2):
        """Calculate how different two texts are (0 to 1)"""
        # Simple character difference ratio
        longer = max(len(text1), len(text2))
        if longer == 0:
            return 0
        return abs(len(text1) - len(text2)) / longer
    
    def calculate_overall_score(self):
        """Calculate overall accessibility score"""
        weighted_score = sum(score * self.weights[category] 
                          for category, score in self.scores.items())
        
        # Round to nearest integer
        return round(weighted_score)
    
    def get_report(self):
        """Generate a detailed accessibility report"""
        overall = self.calculate_overall_score()
        
        report = {
            "overall_score": overall,
            "category_scores": self.scores.copy(),
            "issues": self.issues.copy(),
            "summary": self._get_summary(overall)
        }
        
        return report
    
    def _get_summary(self, score):
        """Get a summary based on the score"""
        if score >= 90:
            return "Excellent accessibility. Minor improvements possible."
        elif score >= 70:
            return "Good accessibility. Some improvements recommended."
        elif score >= 50:
            return "Fair accessibility. Several important issues to address."
        else:
            return "Poor accessibility. Major issues need immediate attention."
    
    def add_score(self, category, score, description):
        """Add a score for a specific category"""
        if category in self.scores:
            current_total = self.scores[category] * self.evaluated_items[category]
            self.evaluated_items[category] += 1
            self.scores[category] = (current_total + score) / self.evaluated_items[category]
            
            # Add to issues if score is below threshold
            if score < 70:
                self.add_issue(category, description)
        
    def add_issue(self, category, description):
        """Add an issue for a specific category"""
        if category in self.issues:
            self.issues[category].append(description)
            
    # Legacy methods for backward compatibility
    def add_alt_text_score(self, has_alt_text, description):
        """Add a score for alt text"""
        score = 100 if has_alt_text else 0
        self.add_score("alt_text", score, description)
        
    def add_font_size_score(self, is_large_enough, description, font_size=None):
        """Add a score for font size"""
        if is_large_enough:
            score = 100
        else:
            # Scale score based on how close it is to the recommended size (18pt)
            score = 100 * (font_size / 18) if font_size else 0
        self.add_score("font_size", score, description)
        
    def add_contrast_score(self, has_good_contrast, description):
        """Add a score for contrast"""
        score = 100 if has_good_contrast else 0
        self.add_score("contrast", score, description)
        
    def add_text_complexity_score(self, is_simple, description):
        """Add a score for text complexity"""
        score = 100 if is_simple else 50  # Not as severe as missing alt text
        self.add_score("text_complexity", score, description) 