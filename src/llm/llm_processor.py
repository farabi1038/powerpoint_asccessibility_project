# src/llm/llm_processor.py
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class LLMProcessor:
    """
    Handles loading the LLM and generating alternative text for images.
    """
    def __init__(self, model_name: str = "stabilityai/stablelm-tuned-alpha-7b"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        # self._load_model()

    def _load_model(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
    
    def generate_alt_text(self, prompt: str, max_tokens: int = 50) -> str:
        """
        Generates alternative text for an image using the LLM.
        """
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=True,
            top_p=0.95,
            temperature=0.7,
            no_repeat_ngram_size=2
        )
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text.strip()
