import json, os, sys
import urllib.request, urllib.error

diff = open('/tmp/pr_diff.txt').read()[:12000]

ac = os.environ.get('AC', 'No acceptance criteria provided.')
jira_key = os.environ.get('JIRA_KEY', 'N/A')
jira_summary = os.environ.get('JIRA_SUMMARY', 'N/A')
tests_passed = os.environ.get('TEST_PASSED', 'false')

# Try Gemini first (free, no IP blocks), then Groq, then DeepSeek
gemini_key = os.environ.get('GEMINI_API_KEY', '')
groq_key = os.environ.get('GROQ_API_KEY', '')
deepseek_key = os.environ.get('DEEPSEEK_API_KEY', '')

print(f"JIRA_KEY: {jira_key}")
print(f"JIRA_SUMMARY: {jira_summary}")
print(f"TEST_PASSED: {tests_passed}")
print(f"AC: {ac[:200]}")
print(f"DIFF size: {len(diff)} chars")

prompt = "\n".join([
    "You are a senior software engineer doing a code review.",
    "",
    f"Jira Ticket: {jira_key}",
    f"Summary: {jira_summary}",
    "",
    "Acceptance Criteria:",
    ac,
    "",
    f"Tests passed: {tests_passed}",
    "",
    "Code Diff:",
    diff,
    "",
    "Return ONLY valid JSON (no markdown, no extra text):",
    '{"overall_status":"APPROVE or REQUEST_CHANGES","summary":"2-3 sentence assessment","meets_acceptance_criteria":true,"comments":[{"file":"path/file.jsx","line":1,"severity":"error|warning|suggestion","message":"comment"}],"approval_reason":"reason"}',
    "",
    "Set overall_status=APPROVE only if: meets_acceptance_criteria=true AND no errors found AND tests_passed=true"
])

def save_result(review):
    json.dump(review, open('/tmp/review_result.json', 'w'), indent=2)
    print(f"Status: {review.get('overall_status')}")
    print(f"Meets AC: {review.get('meets_acceptance_criteria')}")
    print(f"Comments: {len(review.get('comments', []))}")

def fallback_result(reason):
    result = {
        "overall_status": "REQUEST_CHANGES",
        "summary": f"AI review failed: {reason}",
        "meets_acceptance_criteria": False,
        "comments": [],
        "approval_reason": "Automated review could not complete. Please review manually."
    }
    json.dump(result, open('/tmp/review_result.json', 'w'), indent=2)

# ── Try Gemini (free, no IP restrictions) ──
if gemini_key:
    print("Using Gemini API (free)")
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 2000}
        }).encode()

        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            content = result['candidates'][0]['content']['parts'][0]['text'].strip()
            print(f"RAW response:\n{content[:500]}")
            if content.startswith('```'):
                content = content.split('\n', 1)[1].rsplit('```', 1)[0].strip()
            review = json.loads(content)
            save_result(review)
            sys.exit(0)
    except urllib.error.HTTPError as e:
        print(f"Gemini error {e.code}: {e.read().decode()[:200]}")
    except Exception as e:
        print(f"Gemini error: {e}")

# ── Try Groq ──
elif groq_key:
    print("Using Groq API")
    try:
        payload = json.dumps({
            "model": "llama3-70b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 2000
        }).encode()

        req = urllib.request.Request(
            'https://api.groq.com/openai/v1/chat/completions',
            data=payload,
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {groq_key}'}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            content = result['choices'][0]['message']['content'].strip()
            print(f"RAW response:\n{content[:500]}")
            if content.startswith('```'):
                content = content.split('\n', 1)[1].rsplit('```', 1)[0].strip()
            review = json.loads(content)
            save_result(review)
            sys.exit(0)
    except urllib.error.HTTPError as e:
        print(f"Groq error {e.code}: {e.read().decode()[:200]}")
    except Exception as e:
        print(f"Groq error: {e}")

# ── Try DeepSeek ──
elif deepseek_key:
    print("Using DeepSeek API")
    try:
        payload = json.dumps({
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 2000
        }).encode()

        req = urllib.request.Request(
            'https://api.deepseek.com/v1/chat/completions',
            data=payload,
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {deepseek_key}'}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            content = result['choices'][0]['message']['content'].strip()
            print(f"RAW response:\n{content[:500]}")
            if content.startswith('```'):
                content = content.split('\n', 1)[1].rsplit('```', 1)[0].strip()
            review = json.loads(content)
            save_result(review)
            sys.exit(0)
    except urllib.error.HTTPError as e:
        print(f"DeepSeek error {e.code}: {e.read().decode()[:200]}")
    except Exception as e:
        print(f"DeepSeek error: {e}")

else:
    print("ERROR: No API key found. Set GEMINI_API_KEY, GROQ_API_KEY or DEEPSEEK_API_KEY")

fallback_result("No working API key found")
