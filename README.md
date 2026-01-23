# PromptXploit

**LLM Penetration Testing Framework** - Discover vulnerabilities before attackers do

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

⚠️ **[READ DISCLAIMER](./DISCLAIMER.md) - Authorized testing only**

---

## What is PromptXploit?

PromptXploit is a comprehensive security testing framework for LLM applications. Test your AI systems for vulnerabilities **before** deployment.

**Key Features:**
- 🎯 **147 attack vectors** across 17 categories
- 🧠 **AI-powered judge** - Reliable OpenAI-based verdict evaluation
- 🔍 **Batch evaluation** - 10 attacks per API call (efficient)
- 📊 **JSON reporting** - Detailed vulnerability analysis
- 🔌 **Framework-agnostic** - Works with any LLM

---

## Quick Start (30 seconds)

### 1. Install

```bash
git clone https://github.com/Neural-alchemy/promptxploit
cd promptxploit
pip install -e .
```

### 2. Create Target

```python
# my_target.py
def run(prompt: str) -> str:
    # Your LLM here
    return your_llm(prompt)
```

### 3. Run Scan

```bash
python -m promptxploit.main \
    --target my_target.py \
    --attacks attacks/ \
    --output scan.json
```

**Done!** Check `scan.json` for vulnerabilities.

---

## Test ANY API or URL 🌐

**NEW:** You can now test any HTTP endpoint directly!

### Quick API Test

```python
# Edit targets/http_api_target.py
target = HTTPTarget(
    url="https://your-api.com/chat",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    payload_template={"message": "{PAYLOAD}"},
    response_field="response"
)
```

```bash
# Test it
python -m promptxploit.main \
    --target targets/http_api_target.py \
    --attacks attacks/ \
    --output api_scan.json
```

**Works with:**
- ✅ OpenAI ChatGPT API
- ✅ Anthropic Claude API
- ✅ Your custom REST APIs
- ✅ Any HTTP endpoint with input

See [API_TESTING.md](./docs/API_TESTING.md) for full guide.

---

## Attack Taxonomy

PromptXploit tests **147 attacks** across these categories:

```
LLM Attack Surface
├── Prompt Injection (8 variants)
│   ├── Direct instruction override
│   ├── Context confusion
│   └── Delimiter exploitation
├── Jailbreaks (10 variants)
│   ├── DAN (Do Anything Now)
│   ├── Developer mode
│   └── Persona manipulation
├── System Extraction (8 variants)
│   ├── Prompt leakage
│   ├── Configuration disclosure
│   └── Training data extraction
├── Encoding Attacks (8 variants)
│   ├── Base64 obfuscation
│   ├── ROT13/Caesar
│   └── Unicode tricks
├── Multi-Agent Exploitation (10 variants)
│   ├── Tool hijacking
│   ├── Agent confusion
│   └── Coordination attacks
├── RAG Poisoning (8 variants)
│   ├── Context injection
│   ├── Retrieval manipulation
│   └── Source confusion
└── [11 more categories...]
```

---

## Usage

### Quick Test

```bash
# Test your AI application
python -m promptxploit.main \
    --target YOUR_TARGET.py \
    --attacks attacks/ \
    --output results.json
```

That's it! Check `results.json` for vulnerabilities.

### Test Any API

```python
# Edit targets/http_api_target.py
target = HTTPTarget(
    url="https://your-api.com/chat",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    payload_template={"message": "{PAYLOAD}"},
    response_field="response",
    delay_seconds=2.0  # Rate limiting
)
```

```bash
# Test it
python -m promptxploit.main \
    --target targets/http_api_target.py \
    --attacks attacks/ \
    --output results.json
```

**Works with:**
- ✅ OpenAI ChatGPT API
- ✅ Anthropic Claude API
- ✅ Your custom REST APIs
- ✅ Any HTTP endpoint with input

See [API_TESTING.md](./docs/API_TESTING.md) for details.

---

## Real-World Workflow

### Pre-Deployment Testing

```bash
# 1. Test unprotected version
python -m promptxploit.main --target unprotected.py --attacks attacks/ --output before.json

# 2. Review vulnerabilities
cat before.json | jq '.[] | select(.verdict.verdict=="fail")'

# 3. Add PromptShield (our defense framework)
# See: https://github.com/Neural-alchemy/promptshield

# 4. Re-test protected version
python -m promptxploit.main --target protected.py --attacks attacks/ --output after.json

# 5. Verify fixes
diff before.json after.json
```

### Monthly Security Audit

```bash
# Deep scan with adaptive recon
python -m promptxploit.main \
    --mode adaptive \
    --adaptive-strategy recon \
    --probe-diversity 15 \
    --max-iterations 5 \
    --adaptive-api $OPENAI_KEY \
    --target production.py \
    --attacks attacks/ \
    --output audit_$(date +%Y%m%d).json
```

---

## Understanding Results

```json
{
  "attack_id": "JB-003",
  "category": "jailbreak",
  "verdict": {
    "verdict": "fail",        // ⚠️ VULNERABLE
    "confidence": 0.9,
    "severity": 0.9,
    "rationale": "Successfully bypassed restrictions"
  },
  "risk": {
    "risk_score": 0.81,
    "risk_level": "critical"  // 🚨 Fix immediately
  }
}
```

**Verdict types:**
- **FAIL** = Vulnerable (attack succeeded) 🚨
- **PARTIAL** = Uncertain (needs review) ⚠️
- **PASS** = Safe (attack blocked) ✅

---

## Custom Attacks

Create your own attack patterns:

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

```bash
python -m promptxploit.main --target X --attacks my_attacks.json --output Y
```

See [CUSTOM_ATTACKS.md](./docs/CUSTOM_ATTACKS.md) for details.

---

## Integration with PromptShield

**Perfect combo:** Test with PromptXploit → Fix with PromptShield

```python
# Before: Vulnerable
def vulnerable_llm(prompt):
    return openai.chat(prompt)

# After: Protected
from promptshield import Shield
shield = Shield(level=5)

def protected_llm(prompt):
    check = shield.protect_input(prompt, "context")
    if check["blocked"]:
        return "Invalid input"
    return openai.chat(check["secured_context"])
```

Test again with PromptXploit → Verify 100% protection ✅

---

## Why PromptXploit?

**vs. Other Tools:**
- ✅ **Comprehensive** - 147 attacks (others: ~20)
- ✅ **Reliable judge** - OpenAI-based verdict evaluation
- ✅ **Framework-agnostic** - Any LLM (OpenAI, Claude, local, custom)
- ✅ **Easy to extend** - JSON-based attacks
- ✅ **Production-ready** - JSON reporting, CI/CD integration

**vs. Manual testing:**
- ⚡ Automated
- 🎯 Comprehensive coverage
- 📊 Consistent methodology
- 🔁 Repeatable

---

## Responsible Use

⚠️ **This is a security testing tool for authorized use only.**

- ✅ Test your own applications
- ✅ Authorized penetration testing
- ✅ Security research
- ❌ Unauthorized access
- ❌ Malicious attacks

See [DISCLAIMER.md](./DISCLAIMER.md) for full ethical guidelines.

---

## Documentation

- [Attack Taxonomy](./docs/ATTACK_TAXONOMY.md) - All 147 attacks explained
- [Custom Attacks](./docs/CUSTOM_ATTACKS.md) - Create your own tests
- [Responsible Use](./DISCLAIMER.md) - Ethical guidelines
- [Examples](./examples) - Usage examples

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md).

Security researchers: Please follow responsible disclosure practices.

---

## License

MIT License - see [LICENSE](./LICENSE)

---

## Citation

```bibtex
@software{promptxploit2024,
  title={PromptXploit: LLM Penetration Testing Framework},
  author={Neural Alchemy},
  year={2024},
  url={https://github.com/Neural-alchemy/promptxploit}
}
```

---

<div align="center">

**Built by [Neural Alchemy](https://neuralalchemy.ai)**

**Test with PromptXploit | Protect with PromptShield**

[Website](https://neuralalchemy.ai) | [PromptShield](https://github.com/Neural-alchemy/promptshield) | [Documentation](https://neuralalchemy.ai/promptxploit)

</div>
