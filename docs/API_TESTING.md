# Testing ANY API with PromptXploit

This guide shows how to test any HTTP API or URL endpoint for LLM vulnerabilities.

## Quick Start

### 1. Configure Your API

Edit `http_api_target.py` with your API details:

```python
target = HTTPTarget(
    url="https://your-api.com/chat",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    payload_template={"message": "{PAYLOAD}"},
    response_field="response"
)
```

### 2. Run PromptXploit

```bash
python -m promptxploit.main \
    --target targets/http_api_target.py \
    --attacks attacks/ \
    --output api_scan.json
```

---

## Examples

### OpenAI ChatGPT API

```python
from targets.http_api_target import HTTPTarget

target = HTTPTarget(
    url="https://api.openai.com/v1/chat/completions",
    headers={
        "Authorization": "Bearer sk-YOUR_KEY",
        "Content-Type": "application/json"
    },
    payload_template={
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "{PAYLOAD}"}]
    },
    response_field="choices.0.message.content"
)
```

### Anthropic Claude API

```python
target = HTTPTarget(
    url="https://api.anthropic.com/v1/messages",
    headers={
        "x-api-key": "YOUR_KEY",
        "anthropic-version": "2023-06-01"
    },
    payload_template={
        "model": "claude-3-opus-20240229",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": "{PAYLOAD}"}]
    },
    response_field="content.0.text"
)
```

### Custom REST API

```python
target = HTTPTarget(
    url="https://myapp.com/api/chat",
    method="POST",
    headers={"Authorization": "Bearer abc123"},
    payload_template={
        "user_id": "test",
        "message": "{PAYLOAD}",
        "session_id": "xyz"
    },
    response_field="data.response"
)
```

### Simple POST Endpoint

```python
target = HTTPTarget(
    url="https://chatbot.example.com/send",
    payload_template={"text": "{PAYLOAD}"},
    response_field="reply"
)
```

### GET Request with Query Params

```python
target = HTTPTarget(
    url="https://api.example.com/search",
    method="GET",
    payload_template={"q": "{PAYLOAD}"},
    response_field="results"
)
```

---

## Configuration Options

### Required Parameters

- **url**: API endpoint URL
- **payload_template**: Request body with `{PAYLOAD}` placeholder

### Optional Parameters

- **method**: HTTP method (default: "POST")
- **headers**: Authentication, content-type, etc.
- **response_field**: JSON path to response text (e.g., "data.message")

### Response Field Path

Use dot notation to navigate JSON:

```python
# Response: {"choices": [{"message": {"content": "Hello"}}]}
response_field="choices.0.message.content"  # Returns "Hello"

# Response: {"data": {"reply": "Hi there"}}
response_field="data.reply"  # Returns "Hi there"

# Response: {"result": "OK"}
response_field="result"  # Returns "OK"
```

---

## Real-World Testing

### Test Production Chatbot

```bash
# 1. Configure target
vim targets/http_api_target.py

# 2. Run full scan
python -m promptxploit.main \
    --mode static \
    --target targets/http_api_target.py \
    --attacks attacks/ \
    --output production_scan.json

# 3. Check vulnerabilities
cat production_scan.json | jq '.[] | select(.verdict.verdict=="fail")'
```

### Test with Adaptive Mode

```bash
# Intelligent recon-based testing
python -m promptxploit.main \
    --mode adaptive \
    --adaptive-strategy recon \
    --probe-diversity 10 \
    --adaptive-api "YOUR_OPENAI_KEY" \
    --target targets/http_api_target.py \
    --attacks attacks/ \
    --output adaptive_api_scan.json
```

---

## Security Best Practices

⚠️ **Only test APIs you own or have permission to test!**

1. **Get authorization** before testing production systems
2. **Use test endpoints** when available
3. **Rate limit** your requests to avoid overwhelming servers
4. **Monitor costs** when testing paid APIs (OpenAI, Claude, etc.)
5. **Document findings** and report responsibly

---

## Troubleshooting

**Q: Getting 401 Unauthorized?**
→ Check your `Authorization` header and API key

**Q: Response extraction fails?**
→ Verify `response_field` path matches your API's response structure

**Q: Timeout errors?**
→ Increase timeout in `http_api_target.py` (default: 30s)

**Q: Rate limited?**
→ Add delays between requests or reduce attack count

---

## Use Cases

✅ Test your deployed chatbot
✅ Audit third-party AI APIs
✅ Verify AI security before production
✅ Compare different providers' defenses
✅ Research LLM vulnerabilities in the wild

**Now you can test ANY API!** 🎯
