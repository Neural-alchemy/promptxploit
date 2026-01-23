"""
Universal HTTP API Target for PromptXploit

Enables testing ANY API endpoint or URL with input fields.
"""

import requests
import json
from typing import Dict, Any, Optional


class HTTPTarget:
    """Universal HTTP API target adapter"""
    
    def __init__(
        self,
        url: str,
        method: str = "POST",
        headers: Optional[Dict[str, str]] = None,
        payload_template: Optional[Dict[str, Any]] = None,
        payload_field: str = "prompt",
        response_field: Optional[str] = None,
        delay_seconds: float = 0.0  # Rate limiting delay
    ):
        """
        Initialize HTTP target
        
        Args:
            url: API endpoint URL
            method: HTTP method (GET, POST, PUT, etc.)
            headers: HTTP headers (auth, content-type, etc.)
            payload_template: Request body template with {PAYLOAD} placeholder
            payload_field: Field name for attack payload
            response_field: JSON path to extract response
            delay_seconds: Delay between requests (for rate limiting)
        
        Example:
            # With rate limiting (2 second delay)
            target = HTTPTarget(
                url="https://api.openai.com/v1/chat/completions",
                headers={"Authorization": "Bearer sk-..."},
                payload_template={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": "{PAYLOAD}"}]
                },
                response_field="choices.0.message.content",
                delay_seconds=2.0  # Avoid rate limits!
            )
        """
        self.url = url
        self.method = method.upper()
        self.headers = headers or {}
        self.payload_template = payload_template or {}
        self.payload_field = payload_field
        self.response_field = response_field
        self.delay_seconds = delay_seconds
    
    def send(self, prompt: str) -> str:
        """Send attack payload to API"""
        import time
        
        # Rate limiting
        if self.delay_seconds > 0:
            time.sleep(self.delay_seconds)
        
        try:
            # Build request payload
            if self.payload_template:
                # Use template with {PAYLOAD} placeholder
                payload = self._inject_payload(self.payload_template, prompt)
            else:
                # Simple field: {payload_field: prompt}
                payload = {self.payload_field: prompt}
            
            # Send request
            if self.method == "GET":
                response = requests.get(
                    self.url,
                    params=payload,
                    headers=self.headers,
                    timeout=30
                )
            else:  # POST, PUT, etc.
                response = requests.request(
                    self.method,
                    self.url,
                    json=payload,
                    headers=self.headers,
                    timeout=30
                )
            
            response.raise_for_status()
            
            # Extract response
            return self._extract_response(response)
            
        except requests.exceptions.RequestException as e:
            return f"HTTP Error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _inject_payload(self, template: Any, payload: str) -> Any:
        """Recursively inject {PAYLOAD} into template"""
        if isinstance(template, dict):
            return {k: self._inject_payload(v, payload) for k, v in template.items()}
        elif isinstance(template, list):
            return [self._inject_payload(item, payload) for item in template]
        elif isinstance(template, str):
            return template.replace("{PAYLOAD}", payload)
        else:
            return template
    
    def _extract_response(self, response: requests.Response) -> str:
        """Extract text from HTTP response"""
        try:
            data = response.json()
            
            if self.response_field:
                # Navigate JSON path (e.g., "choices.0.message.content")
                result = data
                for key in self.response_field.split("."):
                    if key.isdigit():
                        result = result[int(key)]
                    else:
                        result = result[key]
                return str(result)
            else:
                # Return entire JSON as string
                return json.dumps(data, indent=2)
                
        except (json.JSONDecodeError, KeyError, IndexError, TypeError):
            # Fallback to raw text
            return response.text


# PromptXploit compatible wrapper
def run(prompt: str) -> str:
    """
    Run function for PromptXploit integration
    
    Configure your API below:
    """
    
    # EXAMPLE 1: OpenAI ChatGPT API
    # target = HTTPTarget(
    #     url="https://api.openai.com/v1/chat/completions",
    #     headers={
    #         "Authorization": "Bearer YOUR_KEY_HERE",
    #         "Content-Type": "application/json"
    #     },
    #     payload_template={
    #         "model": "gpt-3.5-turbo",
    #         "messages": [{"role": "user", "content": "{PAYLOAD}"}]
    #     },
    #     response_field="choices.0.message.content"
    # )
    
    # EXAMPLE 2: Claude API
    # target = HTTPTarget(
    #     url="https://api.anthropic.com/v1/messages",
    #     headers={
    #         "x-api-key": "YOUR_KEY_HERE",
    #         "anthropic-version": "2023-06-01"
    #     },
    #     payload_template={
    #         "model": "claude-3-opus-20240229",
    #         "max_tokens": 1024,
    #         "messages": [{"role": "user", "content": "{PAYLOAD}"}]
    #     },
    #     response_field="content.0.text"
    # )
    
    # EXAMPLE 3: Custom API (simple)
    target = HTTPTarget(
        url="https://your-api.com/chat",
        headers={"Authorization": "Bearer YOUR_TOKEN"},
        payload_template={"message": "{PAYLOAD}"},
        response_field="response"
    )
    
    return target.send(prompt)


if __name__ == "__main__":
    # Test the target
    test_prompt = "Hello, how are you?"
    response = run(test_prompt)
    print(f"Prompt: {test_prompt}")
    print(f"Response: {response}")
