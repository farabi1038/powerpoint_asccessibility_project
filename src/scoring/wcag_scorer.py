# src/scoring/scorer.py
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from src.llm.llm_processor import LLMProcessor

class WCAGScorer:
    """
    Analyzes a PowerPoint presentation for accessibility issues based on WCAG 2.1 guidelines.
    Applies fixes using an LLM and computes an overall score.
    """
    def __init__(self, llm_processor: LLMProcessor):
        self.llm_processor = llm_processor
        self.initial_score = 100
        self.score = self.initial_score
        self.issues_log = []

    def analyze_presentation(self, pptx_stream) -> (Presentation, int, list):
        """
        Processes each slide in the presentation.
        Returns the fixed Presentation, final score, and log of issues/fixes.
        """
        prs = Presentation(pptx_stream)
        for slide_index, slide in enumerate(prs.slides, start=1):
            self.analyze_slide(slide, slide_index)
        return prs, self.score, self.issues_log

    def analyze_slide(self, slide, slide_index: int):
        # Initialize variables for each slide.
        slide_title = None
        combined_text = ""
        
        # Check for text content and attempt to detect a slide title.
        for shape in slide.shapes:
            if shape.has_text_frame:
                text = shape.text.strip()
                combined_text += text + " "
                if "title" in shape.name.lower() and not slide_title:
                    slide_title = text
        if not slide_title:
            self.score -= 5
            self.issues_log.append(f"Slide {slide_index}: Missing slide title (-5 points).")
            slide_title = "No Title"

        # Process images: if an image is missing alt text, use the LLM to generate one.
        for shape in slide.shapes:
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                if not shape.alt_text or shape.alt_text.strip() == "":
                    prompt = (
                        f"Generate a concise and descriptive alternative text for an image on a PowerPoint slide. "
                        f"Slide title: '{slide_title}'. Slide text content: '{combined_text.strip()}'."
                    )
                    alt_text = self.llm_processor.generate_alt_text(prompt)
                    shape.alt_text = alt_text
                    self.score -= 10
                    self.issues_log.append(
                        f"Slide {slide_index}: Image missing alt text. Suggestion applied: '{alt_text}' (-10 points)."
                    )

        # Check for tables without header information.
        for shape in slide.shapes:
            if hasattr(shape, "has_table") and shape.has_table:
                table = shape.table
                if table.rows:
                    header_found = any(cell.text.strip() for cell in table.rows[0].cells)
                    if not header_found:
                        self.score -= 5
                        self.issues_log.append(
                            f"Slide {slide_index}: Table missing header row description (-5 points)."
                        )

        # Additional check: flag empty text boxes which may indicate missing descriptions.
        for shape in slide.shapes:
            if shape.has_text_frame:
                if not shape.text.strip():
                    self.score -= 2
                    self.issues_log.append(
                        f"Slide {slide_index}: Text shape is empty, indicating missing description (-2 points)."
                    )
