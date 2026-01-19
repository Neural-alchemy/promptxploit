# rapture/targets/demo_qwen_llama.py
from polyreasoner.app import chat

def run(prompt: str) -> str:
    """
    Rapture target contract:
    MUST return raw model response as string.
    """
    result = chat(prompt)

    if result["status"] == "BLOCKED":
        # IMPORTANT: represent blocks as empty or sentinel text
        return ""

    return result["response"]
