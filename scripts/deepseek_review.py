import json, os, sys
import urllib.request, urllib.error

diff = open('/tmp/pr_diff.txt').read()[:12000]

ac = os.environ.get('AC', 'No acceptance criteria provided.')
jira_key = os.environ.get('JIRA_KEY', 'N/A')
jira_summary = os.environ.get('JIRA_SUMMARY', 'N/A')
# FIX: workflow sends TESTS_PASSED, not TEST_PASSED — support both
tests_passed = os.environ.get('TESTS_PASSED', os.environ.get('TEST_PASSED', 'false'))

gemini_key   = os.environ.get('GEMINI_API_KEY', '')
groq_key     = os.environ.get('GROQ_API_KEY', '')
deepseek_key = os.environ.get('DEEPSEEK_API_KEY', '')

print("=" * 60)
print(f"JIRA_KEY      : {jira_key}")
print(f"JIRA_SUMMARY  : {jira_summary}")
print(f"TESTS_PASSED  : {tests_passed}")
print(f"AC (first 200): {ac[:200]}")
print(f"DIFF size     : {len(diff)} chars")
print(f"GEMINI key    : {'SET' if gemini_key else 'NOT SET'}")
print(f"GROQ key      : {'SET' if groq_key else 'NOT SET'}")
print(f"DEEPSEEK key  : {'SET' if deepseek_key else 'NOT SET'}")
print("=" * 60)

if len(diff.strip()) < 10:
    print("WARNING: diff is empty or very small!")

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
    diff if diff.strip() else "No diff provided - assume code is acceptable.",
    "",
    "Return ONLY valid JSON (no markdown, no extra text):",
    '{"overall_status":"APPROVE or REQUEST_CHANGES","summary":"2-3 sentence assessment","meets_acceptance_criteria":true,"comments":[{"file":"path/file.jsx","line":1,"severity":"error|warning|suggestion","message":"comment"}],"approval_reason":"reason"}',
    "",
    "Set overall_status=APPROVE only if: meets_acceptance_criteria=true AND no errors found AND tests_passed=true"
])


def parse_json(content):
    """Robustly strip markdown fences and parse JSON."""
    content = content.strip()
    # Handle ```json ... ``` or ``` ... ```
    if content.startswith('```'):
        content = content.split('\n', 1)[1] if '\n' in content else ''
        if content.rstrip().endswith('```'):
            content = content.rstrip()[:-3].strip()
    return json.loads(content)


def save_result(review):
    json.dump(review, open('/tmp/review_result.json', 'w'), indent=2)
    print(f"  Status   : {review.get('overall_status')}")
    print(f"  Meets AC : {review.get('meets_acceptance_criteria')}")
    print(f"  Comments : {len(review.get('comments', []))}")
    print(f"  Summary  : {review.get('summary', '')[:200]}")


def fallback_result(reason):
    print(f"\nFALLBACK triggered: {reason}")
    result = {
        "overall_status": "REQUEST_CHANGES",
        "summary": f"AI review failed: {reason}",
        "meets_acceptance_criteria": False,
        "comments": [],
        "approval_reason": "Automated review could not complete. Please review manually."
    }
    json.dump(result, open('/tmp/review_result.json', 'w'), indent=2)


# ── Try Gemini ──────────────────────────────────────────────────────────────
# FIX: was if/elif/elif — if Gemini key exists but fails, Groq/DeepSeek were skipped
# Now each provider is an independent `if` block so all are tried on failure
if gemini_key:
    print("\n[1/3] Trying Gemini API...")
    try:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-1.5-flash:generateContent?key={gemini_key}"
        )
        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 2000}
        }).encode()

        req = urllib.request.Request(
            url, data=payload, headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = json.loads(resp.read())
            content = raw['candidates'][0]['content']['parts'][0]['text']
            print(f"RAW Gemini (first 600 chars):\n{content[:600]}")
            review = parse_json(content)
            save_result(review)
            sys.exit(0)

    except urllib.error.HTTPError as e:
        print(f"  Gemini HTTP {e.code}: {e.read().decode()[:300]}")
    except json.JSONDecodeError as e:
        print(f"  Gemini JSON parse failed: {e}")
    except Exception as e:
        print(f"  Gemini error ({type(e).__name__}): {e}")
    print("  Gemini failed — trying next provider...")


# ── Try Groq ────────────────────────────────────────────────────────────────
if groq_key:
    print("\n[2/3] Trying Groq API...")
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
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {groq_key}'
            }
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = json.loads(resp.read())
            content = raw['choices'][0]['message']['content']
            print(f"RAW Groq (first 600 chars):\n{content[:600]}")
            review = parse_json(content)
            save_result(review)
            sys.exit(0)

    except urllib.error.HTTPError as e:
        print(f"  Groq HTTP {e.code}: {e.read().decode()[:300]}")
    except json.JSONDecodeError as e:
        print(f"  Groq JSON parse failed: {e}")
    except Exception as e:
        print(f"  Groq error ({type(e).__name__}): {e}")
    print("  Groq failed — trying next provider...")


# ── Try DeepSeek ─────────────────────────────────────────────────────────────
if deepseek_key:
    print("\n[3/3] Trying DeepSeek API...")
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
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {deepseek_key}'
            }
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = json.loads(resp.read())
            content = raw['choices'][0]['message']['content']
            print(f"RAW DeepSeek (first 600 chars):\n{content[:600]}")
            review = parse_json(content)
            save_result(review)
            sys.exit(0)

    except urllib.error.HTTPError as e:
        print(f"  DeepSeek HTTP {e.code}: {e.read().decode()[:300]}")
    except json.JSONDecodeError as e:
        print(f"  DeepSeek JSON parse failed: {e}")
    except Exception as e:
        print(f"  DeepSeek error ({type(e).__name__}): {e}")
    print("  DeepSeek failed.")


if not any([gemini_key, groq_key, deepseek_key]):
    print("ERROR: No API key set. Add GEMINI_API_KEY, GROQ_API_KEY or DEEPSEEK_API_KEY to GitHub Secrets.")

fallback_result("All API attempts failed")
