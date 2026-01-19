# Rapture - Quick Start Guide

## Installation

### Option 1: pip install (Recommended)
```bash
pip install rapture-llm
```

### Option 2: From source
```bash
git clone https://github.com/yourusername/rapture
cd rapture
pip install -e .
```

### Dependencies
```
Python >= 3.8
llama-cpp-python (for local LLM mode)
openai (for API mode)
anthropic (for Claude)
rich (for pretty output)
```

**Quick install all:**
```bash
pip install llama-cpp-python openai anthropic rich
```

---

## Quick Start - Test ANY LLM in 60 seconds

### 1. Create Target File

Create `my_target.py`:
```python
def run(prompt: str) -> str:
    """
    Your LLM goes here - Rapture will attack this function
    """
    # Example with OpenAI
    from openai import OpenAI
    client = OpenAI(api_key="your-key")
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

# Or use any LLM: Claude, Gemini, local model, custom API, etc.
```

### 2. Run Static Scan (Basic Test)
```bash
python -m rapture.main \
    --mode static \
    --target my_target.py \
    --attacks rapture/attacks/prompt_extraction \
    --output results.json
```

**Output:**
```
SecurePrompt starting… (mode: static)
✔ Target loaded
Loaded 8 attacks

PE-001 prompt_extraction → FAIL (critical)    # ⚠️ Vulnerable!
PE-002 prompt_extraction → PARTIAL (low)
PE-003 prompt_extraction → PASS (safe)
...

=== Scan Summary ===
Total attacks: 8
Fails: 2        # Your LLM is vulnerable to 2 attacks
Partials: 4
Passes: 2
```

**Done!** You just pentested your LLM.

---

## Advanced Usage

### 1. Full Attack Scan (147 attacks)
```bash
python -m rapture.main \
    --mode static \
    --target my_target.py \
    --attacks rapture/attacks \
    --output full_scan.json
```

### 2. Adaptive Mode - Mutation (Evolve Attacks)
```bash
python -m rapture.main \
    --mode adaptive \
    --adaptive-strategy mutation \
    --adaptive-api "YOUR_OPENAI_KEY" \
    --max-iterations 3 \
    --target my_target.py \
    --attacks rapture/attacks/jailbreak \
    --output adaptive_scan.json
```

**What it does:**
- Tries attack → If blocked, asks GPT to mutate it → Tries again (3x)
- Finds bypasses automatically

### 3. Recon Mode - Intelligence-Based (NEW! ✨)
```bash
python -m rapture.main \
    --mode adaptive \
    --adaptive-strategy recon \
    --probe-diversity 5 \
    --adaptive-api "YOUR_OPENAI_KEY" \
    --max-iterations 3 \
    --target my_target.py \
    --attacks rapture/attacks \
    --output recon_scan.json
```

**What it does:**
1. **Recon:** Tests 5 diverse attacks to learn your defenses
2. **Analyze:** AI analyzes what defenses exist
3. **Craft:** AI creates brand NEW attacks tailored to bypass
4. **Test:** Validates crafted attacks

**This is the most advanced mode!**

---

## Testing Different LLMs

### Test OpenAI
```python
# target_openai.py
from openai import OpenAI

client = OpenAI(api_key="sk-...")

def run(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

```bash
python -m rapture.main --target target_openai.py --attacks rapture/attacks --output openai_scan.json
```

### Test Claude
```python
# target_claude.py
import anthropic

client = anthropic.Anthropic(api_key="sk-...")

def run(prompt: str) -> str:
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
```

### Test Local LLM
```python
# target_local.py
from llama_cpp import Llama

llm = Llama(model_path="path/to/model.gguf")

def run(prompt: str) -> str:
    response = llm(prompt, max_tokens=200)
    return response["choices"][0]["text"]
```

### Test Your Custom AI
```python
# target_custom.py
def run(prompt: str) -> str:
    """
    Put your AI here:
    - REST API call
    - Custom transformer model
    - Ensemble system
    - Multi-agent system
    - Anything that takes prompt → returns text
    """
    response = your_ai_system(prompt)
    return response
```

---

## Understanding Results

### Result File (JSON)
```json
[
  {
    "attack_id": "PE-001",
    "category": "prompt_extraction",
    "verdict": {
      "verdict": "fail",        // ⚠️ VULNERABLE
      "confidence": 0.9,
      "severity": 0.9,
      "rationale": "System prompt disclosed"
    },
    "risk": {
      "risk_score": 0.81,
      "risk_level": "critical"
    }
  }
]
```

### Verdict Types
- **FAIL** = Vulnerable (attack succeeded)
- **PARTIAL** = Uncertain (needs review)
- **PASS** = Safe (attack blocked)

### Risk Levels
- **Critical** = Fix immediately
- **High** = Fix soon
- **Medium** = Monitor
- **Low** = Acceptable risk

---

## Real-World Workflow

### 1. Pre-Deployment Testing
```bash
# Test your chatbot before launch
python -m rapture.main \
    --mode static \
    --target my_chatbot.py \
    --attacks rapture/attacks \
    --output pre_deploy_scan.json

# Review results → Fix vulnerabilities → Re-test
```

### 2. Security Audit
```bash
# Monthly security check
python -m rapture.main \
    --mode adaptive \
    --adaptive-strategy recon \
    --probe-diversity 10 \
    --adaptive-api "KEY" \
    --target production_api.py \
    --attacks rapture/attacks \
    --output monthly_audit.json
```

### 3. Compare Before/After Defense
```bash
# Test unprotected version
python -m rapture.main --target unprotected.py --output before.json

# Add PromptShield
# (see PromptShield quickstart)

# Test protected version
python -m rapture.main --target protected.py --output after.json

# Compare results
```

---

## Attack Categories (147 Total)

1. **prompt_extraction** (8) - Steal system prompts
2. **jailbreak** (10) - Break restrictions
3. **instruction_override** (10) - Ignore instructions
4. **persona_replacement** (7) - Change AI personality
5. **context_confusion** (8) - Confuse the model
6. **encoding** (8) - Bypass via encoding
7. **payload_injection** (5) - Inject malicious content
8. **output_manipulation** (5) - Force specific outputs
9. **adversarial** (10) - Adversarial prompts
10. **agent_manipulation** (10) - Exploit multi-agent
11. **rag_poisoning** (8) - Poison retrieval
12. **training_extraction** (8) - Extract training data
13. **model_fingerprinting** (6) - Identify model
14. **token_smuggling** (8) - Smuggle tokens
15. **system_manipulation** (8) - Manipulate system
16. **response_manipulation** (8) - Control responses
17. **multi_turn** (10) - Multi-turn exploits

---

## CLI Reference

### Required Arguments
```bash
--target PATH          # Path to target file with run() function
--attacks PATH         # Path to attacks directory or file
--output FILE          # Output JSON file
```

### Mode Arguments
```bash
--mode [static|adaptive]              # Attack mode
--adaptive-strategy [mutation|recon]  # Adaptive strategy
--max-iterations N                    # Max mutation attempts (default: 3)
--probe-diversity N                   # Probes for recon (default: 3)
```

### Backend Arguments
```bash
--adaptive-api KEY                    # OpenAI/Claude API key
--adaptive-provider [openai|claude]   # API provider
--adaptive-model PATH                 # Local LLM path
```

---

## Examples

### Quick Test (1 attack category)
```bash
python -m rapture.main \
    --target my_target.py \
    --attacks rapture/attacks/jailbreak \
    --output quick_test.json
```

### Full Production Audit
```bash
python -m rapture.main \
    --mode adaptive \
    --adaptive-strategy recon \
    --probe-diversity 15 \
    --adaptive-api "sk-proj-..." \
    --max-iterations 5 \
    --target production_api.py \
    --attacks rapture/attacks \
    --output full_audit.json
```

### Budget Mode (No API costs)
```bash
python -m rapture.main \
    --mode static \
    --target my_target.py \
    --attacks rapture/attacks \
    --output budget_scan.json
```

---

## Troubleshooting

**Q: Target not loading?**
→ Ensure `run(prompt: str) -> str` function exists

**Q: No attacks found?**
→ Check path to attacks directory

**Q: API errors?**
→ Verify API key and provider

**Q: Slow scans?**
→ Use fewer attack categories or static mode

**Q: Want custom attacks?**
→ Add JSON files to `rapture/attacks/your_category/`

---

## Creating Custom Attacks

```json
[
  {
    "id": "CUSTOM-001",
    "category": "my_category",
    "description": "My custom attack",
    "prompt": "Your attack prompt here"
  }
]
```

Save as `custom_attacks.json` and use:
```bash
python -m rapture.main --target X --attacks custom_attacks.json --output Y
```

---

## Next Steps

1. **Run first scan:** `python -m rapture.main --target ... --attacks ... --output ...`
2. **Review results:** Open output JSON
3. **Fix vulnerabilities:** Add PromptShield or custom defenses
4. **Re-test:** Verify fixes worked
5. **Automate:** Add to CI/CD pipeline

---

## Support

- 📖 Full docs: `rapture/README.md`
- 🔬 How it works: `rapture/HOW_IT_WORKS.md`
- 🧬 Adaptive mode: `rapture/ADAPTIVE_MODE.md`
- 🐛 Issues: GitHub Issues

**Rapture: Intelligent LLM Penetration Testing** 🔥
