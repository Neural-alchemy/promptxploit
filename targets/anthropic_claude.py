# rapture/targets/anthropic_claude.py
"""
Anthropic Claude API target for testing Claude models
Usage: python rapture/main.py --target targets/anthropic_claude.py
"""

import os
from anthropic import Anthropic

# Configuration
API_KEY = os.getenv("ANTHROPIC_API_KEY", "your-api-key-here")
MODEL = "claude-3-5-sonnet-20241022"  # or claude-3-opus, claude-3-haiku
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
        _client = Anthropic(api_key=API_KEY)
        print(f"[TARGET] Anthropic client initialized (model: {MODEL})")
    
    try:
        # Call Anthropic API
        response = _client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text
        
    except Exception as e:
        return f"[ERROR] {str(e)}"


if __name__ == "__main__":
    # Quick test
    test_prompt = "Hello, how are you?"
    response = run(test_prompt)
    print(f"Prompt: {test_prompt}")
    print(f"Response: {response}")
