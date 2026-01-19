# rapture/targets/custom_api_template.py
"""
Template for creating custom API targets
Copy this file and modify for your specific API
"""

import requests

# Configuration - Update these
API_ENDPOINT = "https://your-api.com/v1/chat"
API_KEY = "your-api-key-here"
MODEL = "your-model-name"

def run(prompt: str) -> str:
    """
    Target function called by Rapture for each attack.
    
    Args:
        prompt: Attack payload to test
        
    Returns:
        Model's response as string
    """
    
    try:
        # Example API call structure - modify for your API
        response = requests.post(
            API_ENDPOINT,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 150
            },
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        # Extract response text - modify based on your API's response format
        # Examples:
        # - OpenAI style: data["choices"][0]["message"]["content"]
        # - Claude style: data["content"][0]["text"]
        # - Custom: data["response"]["text"]
        
        return data["response"]  # <-- UPDATE THIS LINE
        
    except requests.exceptions.Timeout:
        return "[ERROR] Request timeout"
    except requests.exceptions.RequestException as e:
        return f"[ERROR] API request failed: {str(e)}"
    except (KeyError, IndexError) as e:
        return f"[ERROR] Unexpected response format: {str(e)}"
    except Exception as e:
        return f"[ERROR] {str(e)}"


if __name__ == "__main__":
    # Quick test
    test_prompt = "Hello, how are you?"
    response = run(test_prompt)
    print(f"Prompt: {test_prompt}")
    print(f"Response: {response}")
