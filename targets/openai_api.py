# rapture/targets/openai_api.py
"""
OpenAI API target for testing GPT-4, GPT-3.5, etc.
Usage: python rapture/main.py --target targets/openai_api.py
"""

import os
from openai import OpenAI

# Configuration
API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")
MODEL = "gpt-4"  # or gpt-3.5-turbo, gpt-4-turbo, etc.
TEMPERATURE = 0.7
MAX_TOKENS = 150

# Initialize client (once)
_client = None

def run(prompt: str) -> str:
    """
    Target function called by Rapture for each attack.
    
    Args:
        prompt: Attack payload to test
        
    Returns:
        Model's response as string
    """
    global _client
    
    # Initialize client once
    if _client is None:
        _client = OpenAI(api_key=API_KEY)
        print(f"[TARGET] OpenAI client initialized (model: {MODEL})")
    
    try:
        # Call OpenAI API
        response = _client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"[ERROR] {str(e)}"


if __name__ == "__main__":
    # Quick test
    test_prompt = "Hello, how are you?"
    response = run(test_prompt)
    print(f"Prompt: {test_prompt}")
    print(f"Response: {response}")
