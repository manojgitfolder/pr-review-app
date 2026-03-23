import json, os, sys
import urllib.request, urllib.error

diff = open('/tmp/pr_diff.txt').read()[:12000]

ac           = os.environ.get('AC', 'No acceptance criteria provided.')
jira_key     = os.environ.get('JIRA_KEY', 'N/A')
jira_summary = os.environ.get('JIRA_SUMMARY', 'N/A')
tests_passed = os.environ.get('TESTS_PASSED', os.environ.get('TEST_PASSED', 'false'))
gemini_key   = os.environ.get('GEMINI_API_KEY', '')

print("=" * 60)
print(f"JIRA_KEY      : {jira_key}")
print(f"JIRA_SUMMARY  : {jira_summary}")
print(f"TESTS_PASSED  : {tests_passed}")
print(f"AC (first 200): {ac[:200]}")
print(f"DIFF size     : {len(diff)} chars")
print(f"GEMINI key    : {'SET (len=' + str(len(gemini_key)) + ')' if gemini_key else 'NOT SET'}")
print("=" * 60)

if not gemini_key:
    print("ERROR: GEMINI_API_KEY is not set.")
    json.dump({
        "overall_status": "REQUEST_CHANGES",
        "summary": "AI review failed: GEMINI_API_KEY secret is not set.",
        "meets_acceptance_criteria": False,
        "comments": [],
        "approval_reason": "Please add GEMINI_API_KEY to GitHub secrets."
    }, open('/tmp/review_result.json', 'w'), indent=2)
    sys.exit(1)

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
    content = content.strip()
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


# Models ordered by free quota availability.
# gemini-2.0-flash-lite has the highest free RPM (30) and TPM.
# gemini-2.5-pro-exp-03-25 is free experimental with generous limits.
# gemini-2.0-flash has lower free quota but still worth trying.
GEMINI_MODELS = [
    "gemini-2.0-flash-lite",        # 30 RPM free — highest free quota
    "gemini-2.5-pro-exp-03-25",     # free experimental model
    "gemini-2.0-flash",             # 15 RPM free
]

for model in GEMINI_MODELS:
    print(f"\nTrying Gemini model: {model}")
    try:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={gemini_key}"
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
            print(f"  RAW response (first 600):\n{content[:600]}")
            review = parse_json(content)
            save_result(review)
            sys.exit(0)

    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(f"  HTTP {e.code}: {err_body[:500]}")
        if e.code in (401, 403):
            print("  Invalid or unauthorized API key. Regenerate at https://aistudio.google.com/apikey")
            break
        # 429 = quota exceeded for this model, try next
        # 404 = model not available, try next
        continue

    except json.JSONDecodeError as e:
        print(f"  JSON parse error: {e}")
        break

    except Exception as e:
        print(f"  Error ({type(e).__name__}): {e}")
        break

print("\nAll Gemini attempts failed.")
print("ACTION REQUIRED: Go to https://aistudio.google.com/apikey and create a new API key,")
print("then update the GEMINI_API_KEY secret in GitHub repo Settings → Secrets.")
json.dump({
    "overall_status": "REQUEST_CHANGES",
    "summary": "AI review failed: Gemini quota exceeded on all models. See workflow logs.",
    "meets_acceptance_criteria": False,
    "comments": [],
    "approval_reason": "Automated review could not complete. Please review manually."
}, open('/tmp/review_result.json', 'w'), indent=2)
