import json, os, sys
import urllib.request, urllib.error

diff = open('/tmp/pr_diff.txt').read()[:12000]

# AC and summary come from env vars (set by workflow from previous step outputs)
ac = os.environ.get('AC', 'No acceptance criteria provided.')
jira_key = os.environ.get('JIRA_KEY', 'N/A')
jira_summary = os.environ.get('JIRA_SUMMARY', 'N/A')
tests_passed = os.environ.get('TEST_PASSED', 'false')
api_key = os.environ.get('DEEPSEEK_API_KEY', '')

if not api_key:
    print("ERROR: DEEPSEEK_API_KEY not set")
    sys.exit(1)

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
        'Authorization': f'Bearer {api_key}'
    }
)

try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read())
        content = result['choices'][0]['message']['content'].strip()
        if content.startswith('```'):
            content = content.split('\n', 1)[1].rsplit('```', 1)[0].strip()
        review = json.loads(content)
        json.dump(review, open('/tmp/review_result.json', 'w'), indent=2)
        print(f"Status: {review.get('overall_status')}, Comments: {len(review.get('comments', []))}")
except Exception as e:
    print(f"DeepSeek error: {e}")
    fallback = {
        "overall_status": "REQUEST_CHANGES",
        "summary": f"AI review failed: {e}",
        "meets_acceptance_criteria": False,
        "comments": [],
        "approval_reason": "Automated review could not complete. Please review manually."
    }
    json.dump(fallback, open('/tmp/review_result.json', 'w'), indent=2)
