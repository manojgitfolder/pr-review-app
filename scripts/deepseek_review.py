import json, os, sys
import urllib.request, urllib.error

diff = open('/tmp/pr_diff.txt').read()[:12000]

ac = os.environ.get('AC', 'No acceptance criteria provided.')
jira_key = os.environ.get('JIRA_KEY', 'N/A')
jira_summary = os.environ.get('JIRA_SUMMARY', 'N/A')
tests_passed = os.environ.get('TEST_PASSED', 'false')

# Support both Groq (free) and DeepSeek
groq_key = os.environ.get('GROQ_API_KEY', '')
deepseek_key = os.environ.get('DEEPSEEK_API_KEY', '')

if groq_key:
    api_key = groq_key
    api_url = 'https://api.groq.com/openai/v1/chat/completions'
    model = 'llama3-70b-8192'
    print("Using Groq API (free)")
elif deepseek_key:
    api_key = deepseek_key
    api_url = 'https://api.deepseek.com/v1/chat/completions'
    model = 'deepseek-chat'
    print("Using DeepSeek API")
else:
    print("ERROR: No API key found. Set GROQ_API_KEY or DEEPSEEK_API_KEY")
    sys.exit(1)

print(f"JIRA_KEY: {jira_key}")
print(f"JIRA_SUMMARY: {jira_summary}")
print(f"TEST_PASSED: {tests_passed}")
print(f"AC: {ac[:200]}")
print(f"DIFF size: {len(diff)} chars")

prompt = "\n".join([
    "You are a senior software engineer doing a code review.",
    "",
    f"## Jira Ticket: {jira_key}",
    f"## Summary: {jira_summary}",
    "",
    "## Acceptance Criteria:",
    ac,
    "",
    f"## Tests passed: {tests_passed}",
    "",
    "## Code Diff:",
    diff,
    "",
    "Return ONLY valid JSON (no markdown, no extra text):",
    '{"overall_status":"APPROVE or REQUEST_CHANGES","summary":"2-3 sentence assessment","meets_acceptance_criteria":true,"comments":[{"file":"path/file.jsx","line":1,"severity":"error|warning|suggestion","message":"comment"}],"approval_reason":"reason"}',
    "",
    "APPROVE only if: meets_acceptance_criteria=true AND no errors AND tests_passed=true"
])

payload = json.dumps({
    "model": model,
    "messages": [{"role": "user", "content": prompt}],
    "temperature": 0.1,
    "max_tokens": 2000
}).encode()

req = urllib.request.Request(
    api_url,
    data=payload,
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
)

try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read())
        content = result['choices'][0]['message']['content'].strip()
        print(f"RAW response:\n{content}")

        if content.startswith('```'):
            content = content.split('\n', 1)[1].rsplit('```', 1)[0].strip()

        review = json.loads(content)
        json.dump(review, open('/tmp/review_result.json', 'w'), indent=2)
        print(f"Status: {review.get('overall_status')}")
        print(f"Meets AC: {review.get('meets_acceptance_criteria')}")
        print(f"Comments: {len(review.get('comments', []))}")

except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"API HTTP error {e.code}: {body}")
    fallback = {
        "overall_status": "REQUEST_CHANGES",
        "summary": f"AI review failed: HTTP {e.code} - {body[:200]}",
        "meets_acceptance_criteria": False,
        "comments": [],
        "approval_reason": "Automated review could not complete. Please review manually."
    }
    json.dump(fallback, open('/tmp/review_result.json', 'w'), indent=2)

except Exception as e:
    print(f"Error: {e}")
    fallback = {
        "overall_status": "REQUEST_CHANGES",
        "summary": f"AI review failed: {e}",
        "meets_acceptance_criteria": False,
        "comments": [],
        "approval_reason": "Automated review could not complete. Please review manually."
    }
    json.dump(fallback, open('/tmp/review_result.json', 'w'), indent=2)
