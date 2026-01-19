# rapture/targets/google_gemini.py
"""
Google Gemini API target for testing Gemini models
Usage: python rapture/main.py --target targets/google_gemini.py
"""

import os
import google.generativeai as genai

# Configuration
API_KEY = os.getenv("GOOGLE_API_KEY", "your-api-key-here")
MODEL = "gemini-pro"  # or gemini-pro-vision, etc.
TEMPERATURE = 0.7
MAX_TOKENS = 150

# Initialize client (once)
_model = None

def run(prompt: str) -> str:
    """
    Target function called by Rapture for each attack.
    
    Args:
        prompt: Attack payload to test
        
    Returns:
        Model's response as string
    """
    global _model
    
    # Initialize client once
    if _model is None:
        genai.configure(api_key=API_KEY)
        _model = genai.GenerativeModel(MODEL)
        print(f"[TARGET] Google Gemini initialized (model: {MODEL})")
    
    try:
        # Call Gemini API
        response = _model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=TEMPERATURE,
                max_output_tokens=MAX_TOKENS
            )
        )
        
        return response.text
        
    except Exception as e:
        return f"[ERROR] {str(e)}"


if __name__ == "__main__":
    # Quick test
    test_prompt = "Hello, how are you?"
    response = run(test_prompt)
    print(f"Prompt: {test_prompt}")
    print(f"Response: {response}")
